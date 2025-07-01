from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from bill.forms import TblTaxEntryForm
from bill.models import (
    Bill,
    BillItem,
    PaymentType,
    TablReturnEntry,
    TblSalesEntry,
    TblTaxEntry,
)
from product.models import Product, BranchStock 
from organization.models import Organization


class PaymentTypeSerializer(ModelSerializer):
    class Meta:
        model = PaymentType
        fields = ["id", "title"]


class BillItemSerializer(ModelSerializer):
    class Meta:
        model = BillItem
        fields = [
            "product_quantity",
            "product",
            "rate",
            "amount",
        ]

from bill.models import BillPayment
class BillPaymentSerializer(ModelSerializer):
    class Meta:
        model = BillPayment
        fields = ['payment_mode', 'rrn', 'amount']
        
from bill.models import MobilePaymentSummary
class MobilePaymentSummarySerializer(ModelSerializer):
    class Meta:
        model = MobilePaymentSummary
        fields = [
            "type",
            "value"
        ]


from user.models import Customer
from bill.utils import product_sold
class BillSerializer(ModelSerializer):
    bill_items = BillItemSerializer(many=True)
    agent = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    split_payment = BillPaymentSerializer(many=True, write_only=True)

    mobile_payments = MobilePaymentSummarySerializer(many=True, write_only=True, required=False)


    class Meta:
        model = Bill
        exclude = [
            "created_at",
            "updated_at",
            "status",
            "is_deleted",
            "sorting_order",
            "is_featured",
            "organization",
        ]

    def create(self, validated_data):
        bill_items = []
        
        payment_data = []
        mobile_payments = validated_data.pop("mobile_payments", [])
        
        items_data = validated_data.pop("bill_items")
        split_payment = validated_data.pop("split_payment")
        
        branch = validated_data.get('branch', None)


        payment_mode = validated_data.get('payment_mode')
        # if not payment_mode.lower() == "complimentary":
        #     bill_count_no = int(validated_data.get('invoice_number').split('-')[-1])
        # else:
        #     bill_count_no = None
        
        if not payment_mode.lower() == "complimentary":
            bill_count_no = int(validated_data.get('invoice_number').split('-')[-1])
            branch_name=branch.branch_code if branch else None
            # invoice_number1 = f"{branch_name}-{terminal}-{bill_count_no}"
            customer_id = validated_data.get('customer')
            if customer_id is not None:
                customer = Customer.objects.get(pk=customer_id.id)
        
                # if loyalty_id is not None:
                #     product_for_points = ProductPoints.objects.get(pk=loyalty_id)
                #     loyaltypoints_tobe_sub = product_for_points.points
                #     starting_points_redeem = customer.loyalty_points
                #     if starting_points_redeem < loyaltypoints_tobe_sub:
                #         raise serializers.ValidationError({"detail":"You do not have sufficient points to claim the reward"})
                #     customer.loyalty_points -= loyaltypoints_tobe_sub
                #     customer.save()
                #     product_redeemed = product_for_points.product
                #     branchstock_entries = BranchStock.objects.filter(branch=branch, product=product_redeemed, is_deleted=False).order_by('quantity')

                #     quantity_decreased = False
                #     for branchstock in branchstock_entries:
                #             available_quantity = branchstock.quantity
                #             if available_quantity > 0 and not quantity_decreased:
                #                 branchstock.quantity -= 1
                #                 branchstock.save()
                #                 quantity_decreased=True

                #     if quantity_decreased == False:
                #         raise serializers.ValidationError({"detail":"The product redeemed has no stock quantities"})
                    # CustomerProductPointsTrack.objects.create(customer=customer, starting_points=starting_points_redeem, points=loyaltypoints_tobe_sub, action="Redeem", bill_no=invoice_number1, remaining_points=customer.loyalty_points)
        
                grand_total = validated_data.get('grand_total')
                loyalty_percentage = Organization.objects.last().loyalty_percentage
                loyalty_points = (loyalty_percentage/100) * grand_total
                # starting_points_reward = customer.loyalty_points
                customer.loyalty_points += loyalty_points
                customer.save()
                # CustomerProductPointsTrack.objects.create(customer=customer, starting_points=starting_points_reward, points=loyalty_points, action="Reward", bill_no=invoice_number1, remaining_points=customer.loyalty_points)
        else:
            bill_count_no = None

        bill = Bill.objects.create(
            **validated_data, organization=Organization.objects.last(), bill_count_number=bill_count_no, print_count=3
        )

        for payment in split_payment:
            BillPayment.objects.create(bill=bill, payment_mode=payment['payment_mode'], rrn=payment['rrn'], amount=payment['amount'])

        
        try:
            for item in items_data:
                quantity = item["product_quantity"]
                product = item["product"]
                bill_item = BillItem.objects.create(
                    product_quantity=item["product_quantity"],
                    rate=item["rate"],
                    product_title=item["product"].title,
                    unit_title=item["product"].unit,
                    amount=item["product_quantity"] * item["rate"],
                    product=item['product']
                )
                org = Organization.objects.first()
                allow_negative_sales = org.allow_negative_sales
                print("I am inside")
                if not allow_negative_sales:
                    branch = validated_data.get('branch')
                    branchstock_entries = BranchStock.objects.filter(branch=branch, product=item['product'], is_deleted=False).order_by('quantity')
        
                    for branchstock in branchstock_entries:
                            if quantity > 0:
                                available_quantity = branchstock.quantity
                                if quantity >= available_quantity:
                                    # Reduce the available quantity to 0 and update the branchstock entry
                                    branchstock.quantity = 0
                                    branchstock.save()
                                    quantity -= available_quantity
                                else:
                                    # Reduce the available quantity by the bill item quantity and update the branchstock entry
                                    branchstock.quantity -= quantity
                                    branchstock.save()
                                    quantity = 0
                
                product_sold(bill_item)

                bill_items.append(bill_item)
            bill.bill_items.add(*bill_items)
        except Exception as E:
            print("Exception ",E)
            
        if payment_mode.lower() == "mobile payment" or payment_mode.lower() == "split":
            try:
                for item in mobile_payments:
                    mobile_payment = MobilePaymentSummary.objects.create(
                        type = item["type"],
                        value = item["value"],
                        bill= bill,
                        branch=validated_data.get('branch'),
                        terminal = validated_data.get('terminal')
                    )

                    payment_data.append(mobile_payment)
            except Exception as E:
                print("Exception ",E)        
        
        return bill


class BillDetailSerializer(ModelSerializer):
    bill_items = BillItemSerializer(many=True)
    agent = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Bill
        fields = "__all__"


class TblTaxEntrySerializer(ModelSerializer):
    reason = serializers.CharField(required=False)

    class Meta:
        model = TblTaxEntry
        fields = "__all__"

    def update(self, instance, validated_data):
        is_active_data = validated_data.get("is_active")
        reason = validated_data.get("reason")
        print("/n/n")
        print(instance.bill_no)
        print(instance.customer_pan)

        if is_active_data == "no":
            miti = ""
            quantity = 1
            try:
                print("TRY VITRA XU MA\n\n")
                obj = TblSalesEntry.objects.get(
                    bill_no=instance.bill_no, customer_pan=instance.customer_pan
                )
                print(obj)

                obj = Bill.objects.get(
                    invoice_number=instance.bill_no,
                    customer_tax_number=instance.customer_pan,
                )
                obj.status = False
                obj.save()
                # obj.save()

                print(obj)
                miti = obj.transaction_miti
                quantity = obj.bill_items.count()

                return_entry = TablReturnEntry(
                    bill_date=instance.bill_date,
                    bill_no=instance.bill_no,
                    customer_name=instance.customer_name,
                    customer_pan=instance.customer_pan,
                    amount=instance.amount,
                    NoTaxSales=0,
                    ZeroTaxSales=0,
                    taxable_amount=instance.taxable_amount,
                    tax_amount=instance.tax_amount,
                    miti=miti,
                    ServicedItem="Goods",
                    quantity=quantity,
                    reason=reason,
                )
                print(return_entry)
                return_entry.save()

            except:
                print("exception")
        instance.save()

        return super().update(instance, validated_data)


class TblTaxEntryVoidSerializer(ModelSerializer):
    reason = serializers.CharField(required=False)
    trans_date = serializers.CharField(required=True)
    class Meta:
        model = TblTaxEntry
        exclude = 'fiscal_year',


class TblSalesEntrySerializer(ModelSerializer):
    class Meta:
        model = TblSalesEntry
        fields = "__all__"


class TablReturnEntrySerializer(ModelSerializer):
    class Meta:
        model = TablReturnEntry
        fields = "__all__"
