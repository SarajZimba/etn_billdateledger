from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from rest_framework import routers

from ..views.user import CustomTokenObtainPairView, CustomerAPI

from ..views.user import AgentViewSet


router = routers.DefaultRouter()
router.register('agent-create', AgentViewSet, basename='agent')


router.register("customer", CustomerAPI)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
] + router.urls
