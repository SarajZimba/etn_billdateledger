from api.views.endday_report import EndDayReportDayWiseAPIView, EndDayReportAPIView
from django.urls import path

# router.register("customer-product-list", CustomerProductAPI)

urlpatterns = [
    path("enddayreport-list/", EndDayReportAPIView.as_view(), name="enddayreport_list"),
    path("enddayreport-list-daywise/", EndDayReportDayWiseAPIView.as_view(), name="enddayreport_list"),



    # path("product-categories", CategoryAPIView.as_view(), name="product-categories")

] 
 
