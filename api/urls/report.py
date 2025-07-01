from django.urls import path
from api.views.report import SummaryReport, MasterBillDetailView, BillDetailView, CustomerBills

urlpatterns = [
    path("summary-report/", SummaryReport.as_view(), name="summary-report"),

    path('bill-endday/', BillDetailView.as_view(), name='bill-detail'),

    path('master-bill-endday/', MasterBillDetailView.as_view(), name='bill-detail'),

    path('customer-bills/', CustomerBills.as_view(), name='customer-bills')

    # path("product-categories", CategoryAPIView.as_view(), name="product-categories")

] 