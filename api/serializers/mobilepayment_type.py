from rest_framework.serializers import ModelSerializer
from bill.models import MobilePaymentType
from rest_framework import serializers
import base64

class MobilePaymentTypeSerializerCreate(ModelSerializer):
    # icon = serializers.SerializerMethodField()
    class Meta:
        model=MobilePaymentType
        exclude = [
            "created_at",
            "updated_at",
            "status",
            "is_deleted",
            "sorting_order",
            "is_featured"
        ]
        
    # def get_icon(self, obj):
    #     if obj.icon:
    #         try:
    #             with open(obj.icon.path, "rb") as image_file:
    #                 encoded_string = base64.b64encode(image_file.read())
    #                 decoded_string = encoded_string.decode('utf-8')
    #                 return decoded_string
    #         except Exception as e:
    #             print(f"Error encoding the image for {obj}")
    #     return None
        
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
        
    
    
class MobilePaymentSerializer(ModelSerializer):
    # category = ProductCategorySerializer()

    # ledger_name = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    qr = serializers.SerializerMethodField()    
    class Meta:
        model = MobilePaymentType
        exclude = [
            "created_at",
            "updated_at",
            "status",
            "is_deleted",
            "sorting_order",
            "is_featured"
        ]

    def get_icon(self, obj):
        if obj.icon:
            try:
                with open(obj.icon.path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read())
                    decoded_string = encoded_string.decode('utf-8')
                    return decoded_string
            except Exception as e:
                print(f"Error encoding the image for {obj}")
        return None
        
    def get_qr(self, obj):
        if obj.icon:
            try:
                with open(obj.qr.path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read())
                    decoded_string = encoded_string.decode('utf-8')
                    return decoded_string
            except Exception as e:
                print(f"Error encoding the image for {obj}")
        return None
    # def get_ledger_name(self, obj):
    #     # Check if the ledger field is not None
    #         if obj.ledger:
    #             return obj.ledger.ledger_name
    #         else:
    #             return None  # Return None if ledger is None