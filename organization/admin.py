from django.contrib import admin

# Register your models here.
from .models import Organization, Branch

admin.site.register([Organization, Branch])
