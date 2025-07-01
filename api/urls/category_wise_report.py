from api.views.category_wise_report import CategoryWiseSaleAPIView
from django.urls import path

# router.register("customer-product-list", CustomerProductAPI)

urlpatterns = [
    path("categorywise-salelist/", CategoryWiseSaleAPIView.as_view(), name="categorywise-salelist"),

] 
 
