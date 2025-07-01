from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(AccountChart)
admin.site.register(AccountLedger)
admin.site.register(AccountSubLedger)