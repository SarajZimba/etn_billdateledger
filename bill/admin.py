from django.contrib import admin

from .models import (
    Bill,
    PaymentType,
    BillItem,
    TblTaxEntry,
    TblSalesEntry,
    TablReturnEntry,
)

admin.site.register(
    [Bill, PaymentType, BillItem, TblTaxEntry, TblSalesEntry, TablReturnEntry]
)
