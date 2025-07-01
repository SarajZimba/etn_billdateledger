from django.contrib import admin
from .models import Vendor, Purchase, ProductPurchase

admin.site.register([Vendor, Purchase, ProductPurchase])
