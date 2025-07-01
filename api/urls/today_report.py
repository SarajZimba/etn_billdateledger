from api.views.today_report import TodaysTransactionAPIView
from django.urls import path

# router.register("customer-product-list", CustomerProductAPI)

urlpatterns = [
    path("today-report/", TodaysTransactionAPIView.as_view(), name="today_list"),



    # path("product-categories", CategoryAPIView.as_view(), name="product-categories")

] 
 
