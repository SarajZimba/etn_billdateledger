from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models import Customer


User = get_user_model()

import json


class CustomTokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["name"] = user.full_name
        groups = []
        for group in user.groups.values_list("name"):
            groups.append(group[0])
        group_str = json.dumps(groups)
        token["role"] = group_str

        return token


class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        exclude = [
            "created_at",
            "updated_at",
            "status",
            "is_deleted",
            "sorting_order",
            "is_featured",
            "created_by",
        ]
