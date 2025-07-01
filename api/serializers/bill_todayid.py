# serializers.py
from rest_framework import serializers
from bill.models import Bill, BillItem

class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        exclude = [
            "created_at",
            "updated_at",
            "status",
            "is_deleted",
            "sorting_order",
            "is_featured",
            "unit_title",
            "is_taxable",
            "agent",
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Remove the first "/" from the image URL
       
        data['rate'] = round(float(data['rate']), 2)
        data['amount'] = round(float(data['amount']), 2)
        # if 'straintype' in data:
        #     data['category'] = data.pop('straintype')
        return data

class BillSerializer(serializers.ModelSerializer):
    bill_items = BillItemSerializer(many=True)
    class Meta:
        model = Bill
        exclude = [
            "created_at",
            "updated_at",
            "status",
            "is_deleted",
            "sorting_order",
            "is_featured",
            "transaction_miti"
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Remove the first "/" from the image URL
       
        data['sub_total'] = round(float(data['sub_total']), 2)
        data['discount_amount'] = round(float(data['discount_amount']), 2)
        data['taxable_amount'] = round(float(data['taxable_amount']), 2)
        data['tax_amount'] = round(float(data['tax_amount']), 2)
        data['grand_total'] = round(float(data['grand_total']), 2)
        data['service_charge'] = round(float(data['service_charge']), 2)
        # if 'straintype' in data:
        #     data['category'] = data.pop('straintype')
        return data
