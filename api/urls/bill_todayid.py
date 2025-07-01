# urls.py
from django.urls import path
from api.views.bill_todayid import BillDetailView

urlpatterns = [
    # Other URL patterns
    path('bill-today-details/<int:id>/', BillDetailView.as_view(), name='bill-today-details'),
]