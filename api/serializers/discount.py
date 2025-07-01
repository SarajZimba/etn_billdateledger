from discount.models import DiscountTable
from rest_framework.serializers import ModelSerializer


class DiscountSerilizer(ModelSerializer):
    class Meta:
        model = DiscountTable
        fields = "__all__"
