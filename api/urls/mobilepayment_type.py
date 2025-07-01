from api.views.mobilepayment_type import MobilePaymentTypeCreateAPIView, MobilePaymentTypeUpdateAPIView, MobilePaymentTypeDeleteAPIView,\
MobilePaymentTypeDetail, MobilePaymentTypeList
from django.urls import path



from rest_framework import routers

router = routers.DefaultRouter()
# router.register("customer-product-list", CustomerProductAPI)

urlpatterns = [
    path("mobilepaymenttype-list/", MobilePaymentTypeList.as_view(), name="api_mobilepaymenttype_list"),
    path("mobilepaymenttype-detail/<int:pk>", MobilePaymentTypeDetail.as_view(), name="api_mobilepaymenttype_detail"), 
    path("mobilepaymenttype-create/", MobilePaymentTypeCreateAPIView.as_view(), name="mobilepaymenttype-create"),
    path('mobilepaymenttype-update/<int:pk>/', MobilePaymentTypeUpdateAPIView.as_view(), name='mobilepaymenttype-update'),
    path('mobilepaymenttype-delete/<int:pk>/', MobilePaymentTypeDeleteAPIView.as_view(), name='mobilepaymenttype-delete'),


    # path("product-categories", CategoryAPIView.as_view(), name="product-categories")

] + router.urls
 
