from ..views.discount_amount import  DiscountApiView
from django.urls import path

urlpatterns = [
    path("getdiscountlist",DiscountApiView,name="disount-type")
]
