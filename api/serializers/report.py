from organization.models import EndDayDailyReport

from rest_framework import serializers

class EnddaySerializer(serializers.ModelSerializer):
    class Meta:
        model=EndDayDailyReport
        exclude = [
            "created_at",
            "updated_at",
            "status",
            "is_deleted",
            "sorting_order",
            "is_featured"
        ]

class PaymentModeSerializer(serializers.Serializer):
    payment_mode = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=9, decimal_places=2, coerce_to_string=False)


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
       
        data['rate'] = round(float(data['rate']), 2)
        data['amount'] = round(float(data['amount']), 2)
        return data

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill

        fields = ['invoice_number', 'created_at', 'payment_mode', 'grand_total', 'status', 'customer_name', 'id']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['grand_total'] = round(float(data['grand_total']), 2)
        if  data['status'] == False:
            data['payment_mode'] = "VOID"

        return data
    
    

    




