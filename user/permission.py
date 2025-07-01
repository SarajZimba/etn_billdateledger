from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from datetime import datetime, timedelta


class CheckPermissionMixin(object):
    perm_group = [
        "admin",
    ]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name__in=self.perm_group).exists():
                return super().dispatch(request, *args, **kwargs)
        return redirect(reverse_lazy("user:login_view"))


class SearchMixin:
    search_lookup_fields = []
    valid_date_filter = ["created_at", "-created_at", "updated_at", "-updated_at"]

    def get_queryset(self, *args, **kwargs):
        qc = super().get_queryset(*args, **kwargs)
        qc = self.search(qc)
        qc = self.date_filter(qc)
        qc = self.date_range_filter(qc)
        return qc

    def date_filter(self, qc):
        if self.request.GET.get("sort_date"):
            sort_date = self.request.GET.get("sort_date")
            if sort_date in self.valid_date_filter:
                return qc.order_by(sort_date)
        return qc

    # def date_range_filter(self, qc):
    #     if self.request.GET.get("fromDate") and self.request.GET.get("toDate"):
    #         created_at_date = self.request.GET.get("fromDate")
    #         created_to_date = self.request.GET.get("toDate")
    #         return qc.filter(created_at__range=[created_at_date, created_to_date])
    #     return qc
    
    def date_range_filter(self, qc):
        
        if self.request.GET.get("fromDate") and self.request.GET.get("toDate"):
            created_at_date = self.request.GET.get("fromDate")
            created_to_date = self.request.GET.get("toDate")
            created_to_date_obj = datetime.strptime(created_to_date, '%Y-%m-%d')

            # Add one day to the created_to_date
            created_to_date_obj += timedelta(days=1)

            # Convert the datetime object back to a string in the same format
            created_to_date_with_one_day_added = created_to_date_obj.strftime('%Y-%m-%d')
            # from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            # to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')

            # # Add one day to the 'to_date'
            # one_day = timedelta(days=1)
            # to_date_obj += one_day

            # # Convert the datetime objects back to strings in the same format
            # from_date = from_date_obj.strftime('%Y-%m-%d')
            # to_date = to_date_obj.strftime('%Y-%m-%d')
            # print("from_date", from_date)
            # print("to_date", to_date)
            # print(qc.filter(created_at__range=[created_at_date, created_to_date_with_one_day_added]))
            # return qc.filter(created_at__range=[created_at_date, created_to_date])
            return qc.filter(created_at__range=[created_at_date, created_to_date_with_one_day_added])
        return qc

    def search(self, qc):
        if self.request.GET.get("q"):
            query = self.request.GET.get("q")
            q_lookup = Q()
            for field in self.search_lookup_fields:
                q_lookup |= Q(**{field + "__icontains": query})
            return qc.filter(q_lookup)
        return qc


class BillFilterMixin:
    search_lookup_fields = [
        # "customer_name",
        # "miti",
        # "bill_no",
        # "customer_pan",
        "customer_name",
        "invoice_number",
        "customer_tax_number",
        "terminal",
    ]

    def get_queryset(self, *args, **kwargs):
        qc = super().get_queryset(*args, **kwargs)
        qc = self.search(qc)
        return qc

    def search(self, qc):
        if self.request.GET.get("q"):
            query = self.request.GET.get("q")
            q_lookup = Q()
            for field in self.search_lookup_fields:
                q_lookup |= Q(**{field + "__icontains": query})
            return qc.filter(q_lookup)
        return qc


# this checks if the user is in group Admin or not
class IsAdminMixin(SearchMixin, object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name="admin").exists():
                return super().dispatch(request, *args, **kwargs)
            return redirect(reverse_lazy("bill_list"))
        return redirect(reverse_lazy("user:login_view"))

class AdminBillingMixin(SearchMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name__in=["admin", "billing_group"]).exists():
                return super().dispatch(request, *args, **kwargs)
        return redirect(reverse_lazy("user:login_view"))


class IsAccountantMixin(BillFilterMixin, object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name="admin").exists():
                return super().dispatch(request, *args, **kwargs)
        return redirect(reverse_lazy("user:login_view"))
        
class PartySearchMixin:
    search_lookup_fields = []
    valid_date_filter = ["bill_date "]

    def get_queryset(self, *args, **kwargs):
        qc = super().get_queryset(*args, **kwargs)
        qc = self.search(qc)
        qc = self.date_filter(qc)
        qc = self.date_range_filter(qc)
        return qc

    def date_filter(self, qc):
        if self.request.GET.get("sort_date"):
            sort_date = self.request.GET.get("sort_date")
            if sort_date in self.valid_date_filter:
                return qc.order_by(sort_date)
        return qc

    # def date_range_filter(self, qc):
    #     if self.request.GET.get("fromDate") and self.request.GET.get("toDate"):
    #         created_at_date = self.request.GET.get("fromDate")
    #         created_to_date = self.request.GET.get("toDate")
    #         return qc.filter(created_at__range=[created_at_date, created_to_date])
    #     return qc
    
    def date_range_filter(self, qc):
        
        if self.request.GET.get("fromDate") and self.request.GET.get("toDate"):
            created_at_date = self.request.GET.get("fromDate")
            created_to_date = self.request.GET.get("toDate")
            created_to_date_obj = datetime.strptime(created_to_date, '%Y-%m-%d')

            # Add one day to the created_to_date
            created_to_date_obj += timedelta(days=1)

            # Convert the datetime object back to a string in the same format
            created_to_date_with_one_day_added = created_to_date_obj.strftime('%Y-%m-%d')
            # from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            # to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')

            # # Add one day to the 'to_date'
            # one_day = timedelta(days=1)
            # to_date_obj += one_day

            # # Convert the datetime objects back to strings in the same format
            # from_date = from_date_obj.strftime('%Y-%m-%d')
            # to_date = to_date_obj.strftime('%Y-%m-%d')
            # print("from_date", from_date)
            # print("to_date", to_date)
            # print(qc.filter(created_at__range=[created_at_date, created_to_date_with_one_day_added]))
            # return qc.filter(created_at__range=[created_at_date, created_to_date])
            return qc.filter(bill_date__range=[created_at_date, created_to_date_with_one_day_added])
        return qc

    def search(self, qc):
        if self.request.GET.get("q"):
            query = self.request.GET.get("q")
            q_lookup = Q()
            for field in self.search_lookup_fields:
                q_lookup |= Q(**{field + "__icontains": query})
            return qc.filter(q_lookup)
        return qc
    

class PartyAdminBillingMixin(PartySearchMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name__in=["admin", "billing_group"]).exists():
                return super().dispatch(request, *args, **kwargs)
        return redirect(reverse_lazy("user:login_view"))
