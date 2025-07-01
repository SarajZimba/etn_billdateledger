from import_export import resources
import tablib

from .models import TblTaxEntry, TblSalesEntry, TablReturnEntry
from organization.models import Organization


class ExportMixin:
    def export(self, queryset=None, *args, **kwargs):
        organization = Organization.objects.last()

        self.before_export(queryset, *args, **kwargs)

        data = tablib.Dataset()
        if queryset is None:
            queryset = self.get_queryset()
        headers = self.get_export_headers()
        data.append_separator(organization.org_name)
        data.append_separator(organization.company_address)
        data.append_separator("")
        data.headers = headers
        print(headers)

        for obj in self.iter_queryset(queryset):
            data.append(self.export_resource(obj))

        self.after_export(queryset, data, *args, **kwargs)

        return data

    def after_export(self, queryset, data, *args, **kwargs):
        export_data = super().after_export(queryset, data, *args, **kwargs)
        data.title = self.title
        return data


class TblTaxEntryResource(ExportMixin, resources.ModelResource):
    title = "Materialized List"

    class Meta:
        model = TblTaxEntry


class SalesEntryResource(ExportMixin, resources.ModelResource):
    title = "Sales Entry List"

    class Meta:
        model = TblSalesEntry


class ReturnEntryResource(ExportMixin, resources.ModelResource):
    title = "Bill Return List"

    class Meta:
        model = TablReturnEntry
