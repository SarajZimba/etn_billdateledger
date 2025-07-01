from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from rest_framework import routers

from ..views.master import CustomTokenObtainPairView

router = routers.DefaultRouter()


urlpatterns = [
    path("master-login/", CustomTokenObtainPairView.as_view(), name="master-login"),
    path("master-token/refresh/", TokenRefreshView.as_view(), name="master-token_refresh"),
] + router.urls
