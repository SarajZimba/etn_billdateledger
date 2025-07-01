from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from user.models import Customer
from ..serializers.master import CustomTokenPairSerializer, CustomerSerializer

from rest_framework.viewsets import ModelViewSet

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenPairSerializer


class CustomerAPI(ModelViewSet):
    serializer_class = CustomerSerializer
    model = Customer
    queryset = Customer.objects.active()
    pagination_class = None
