from django.conf import settings
import environ 
import os
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(settings.BASE_DIR, ".env"))

from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from datetime import date
from django.shortcuts import render
from root.utils import DeleteMixin
from user.models import Customer, User
from user.permission import IsAdminMixin

from .forms import OrganizationForm, StaticPageForm
from .models import Organization, StaticPage


class IndexView(TemplateView):
    template_name = "index.html"


class OrganizationMixin(IsAdminMixin):
    model = Organization
    form_class = OrganizationForm
    paginate_by = 50
    queryset = Organization.objects.filter(status=True, is_deleted=False)
    success_url = reverse_lazy("org:organization_detail")


class OrganizationDetail(OrganizationMixin, DetailView):
    template_name = "organization/organization_detail.html"

    def get_object(self):
        return Organization.objects.last()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.all()
        branches = Branch.objects.filter(
            is_deleted=False, organization=self.get_object().id
        )
        customers = Customer.objects.filter(is_deleted=False)
        context["branches"] = branches
        context["customers"] = customers
        context["users"] = users

        return context


class OrganizationCreate(OrganizationMixin, CreateView):
    template_name = "create.html"


class OrganizationUpdate(OrganizationMixin, UpdateView):
    template_name = "update.html"

    def get_object(self):
        return Organization.objects.last()


class OrganizationDelete(OrganizationMixin, DeleteMixin, View):
    pass


class StaticPageMixin(IsAdminMixin):
    model = StaticPage
    form_class = StaticPageForm
    paginate_by = 50
    queryset = StaticPage.objects.filter(status=True, is_deleted=False)
    success_url = reverse_lazy("org:staticpage_list")
    search_lookup_fields = ["name", "content", "slug", "keywords"]


class StaticPageList(StaticPageMixin, ListView):
    template_name = "staticpage/staticpage_list.html"
    queryset = StaticPage.objects.filter(status=True, is_deleted=False)


class StaticPageDetail(StaticPageMixin, DetailView):
    template_name = "staticpage/staticpage_detail.html"


class StaticPageCreate(StaticPageMixin, CreateView):
    template_name = "create.html"


class StaticPageUpdate(StaticPageMixin, UpdateView):
    template_name = "update.html"


class StaticPageDelete(StaticPageMixin, DeleteMixin, View):
    pass


from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from root.utils import DeleteMixin
from .models import Branch
from .forms import BranchForm


class BranchMixin(IsAdminMixin):
    model = Branch
    form_class = BranchForm
    paginate_by = 50
    queryset = Branch.objects.filter(status=True, is_deleted=False)
    success_url = reverse_lazy("org:branch_list")
    search_lookup_fields = ["name", "address", "contact_number", "branch_manager"]


class BranchList(BranchMixin, ListView):
    template_name = "branch/branch_list.html"
    queryset = Branch.objects.filter(status=True, is_deleted=False)


class BranchDetail(BranchMixin, DetailView):
    template_name = "branch/branch_detail.html"


class BranchCreate(BranchMixin, CreateView):
    template_name = "create.html"

    def form_valid(self, form):
        form.instance.organization = self.request.user.organization
        return super().form_valid(form)


class BranchUpdate(BranchMixin, UpdateView):
    template_name = "update.html"


class BranchDelete(BranchMixin, DeleteMixin, View):
    pass

import mysql.connector

mydb = mysql.connector.connect(
    host="localhost", user=env('DB_USERNAME'), password=env('DB_PASSWORD'), database=env('DB_NAME')
)


def dicfetchall(cursor):
    try:
        desc = cursor.description
    except Exception as e:
        print(e)
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
def gendata(sql):
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    data = dicfetchall(mycursor)
    return data
    
    
def reportView(request, outlet):
    outlet=outlet.replace("%20"," ")
    date1 = request.GET.get("datefirst", date.today())
    date2 = request.GET.get("datesecond", date.today())
    context = {}
    sql = f"SELECT a.description, a.itemName, a.itemrate ,sum(a.count) as count, sum(a.total)as revenu FROM `tblorder_detailshistory` a, tblorderhistory b WHERE a.order_ID = b.idtblorderHistory and b.Date between '{date1}' and '{date2}' and  b.Outlet_Name='{outlet}' and ItemType ='Food' group by a.itemName, a.description, a.itemRate order by a.description, a.itemName, a.count DESC; "
    sql2 = f"SELECT a.description, a.itemName, a.itemrate ,sum(a.count)as count, sum(a.total) as revenu FROM `tblorder_detailshistory` a, tblorderhistory b WHERE a.order_ID = b.idtblorderHistory and b.Date between '{date1}' and '{date2}' and  b.Outlet_Name='{outlet}' and ItemType !='Food' group by a.itemName, a.description, a.itemRate order by a.description, a.itemName, a.count DESC;"
    sql3 = f"SELECT date, bill_no,(total-serviceCharge-VAT) as subtotal,DiscountAmt, serviceCharge, vat, Total, PaymentMode, GuestName FROM `tblorderhistory` WHERE date BETWEEN '{date1}' and '{date2}' and  Outlet_Name='{outlet}' and bill_no!=\"\" order by date; "
    context["tblorder"] = gendata(sql)
    context["tblorder2"] = gendata(sql2)
    context["tblorder3"] = gendata(sql3)
    context["outlet"] = outlet
    try:
        context["date1"] = date1.strftime("%d %b, %Y")
        context["date2"] = date2.strftime("%d %b, %Y")
    except:
        date1=date.today()
        date2=date.today()
    return render(request, "salesreport/report.html", context)


def getoutletName(request):
    context = {}
    sql = f"SELECT DISTINCT Outlet_Name FROM `tblorderhistory`;"
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    data = dicfetchall(mycursor)
    context["outlet_name"] = data
    return render(request, "salesreport/salesoutlate.html", context)


from .models import MailRecipient, EndDayDailyReport
from .forms import MailRecipientForm
class MailRecipientMixin:
    model = MailRecipient
    form_class = MailRecipientForm
    paginate_by = 10
    queryset = MailRecipient.objects.all()
    success_url = reverse_lazy('org:mailrecipient_list')

class MailRecipientList(MailRecipientMixin, ListView):
    template_name = "mailrecipient/mailrecipient_list.html"
    queryset = MailRecipient.objects.filter(status=True)

class MailRecipientDetail(MailRecipientMixin, DetailView):
    template_name = "mailrecipient/mailrecipient_detail.html"

class MailRecipientCreate(MailRecipientMixin, CreateView):
    template_name = "create.html"

class MailRecipientUpdate(MailRecipientMixin, UpdateView):
    template_name = "update.html"

class MailRecipientDelete(MailRecipientMixin, View):
    def remove_from_DB(self, request):
        try:
            print("Object deleted")
            object_id = request.GET.get("pk", None)
            object = self.model.objects.get(id=object_id)
            object.status = False
            object.save()
            return True
        except Exception as e:
            print(e)
            return str(e)
        
    def get(self, request):
        status = self.remove_from_DB(request)
        return JsonResponse({"deleted": status})
    # pass

from .models import Terminal
from .forms import TerminalForm
from accounting.models import AccountLedger, AccountSubLedger
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from typing import Any

class TerminalMixin:
    model = Terminal
    form_class = TerminalForm
    paginate_by = 10
    queryset = Terminal.objects.filter(status=True,is_deleted=False)
    success_url = reverse_lazy('org:terminal_list')

class TerminalList(TerminalMixin, ListView):
    template_name = "terminal/terminal_list.html"
    queryset = Terminal.objects.filter(status=True,is_deleted=False)

class TerminalDetail(TerminalMixin, DetailView):
    pass
    # template_name = "terminal/terminal_detail.html"

class TerminalCreate(TerminalMixin, CreateView):
    template_name = "create.html"

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        cash_in_hand = AccountLedger.objects.get(ledger_name__iexact="cash-in-hand")
        card_transactions = AccountLedger.objects.get(ledger_name__iexact="card transactions")
        mobile_palyemnts = AccountLedger.objects.get(ledger_name__iexact="mobile payments")
        sales = AccountLedger.objects.get(ledger_name__iexact="sales")

        branch_code = get_object_or_404(Branch, pk=int(request.POST.get('branch'))).branch_code
        terminal_no = request.POST.get('terminal_no')

        ledgers = [cash_in_hand, card_transactions, mobile_palyemnts, sales]

        for led in ledgers:
            AccountSubLedger.objects.create(sub_ledger_name=f'{led.ledger_name} {branch_code}-{terminal_no}', ledger=led, is_editable=False)

        return super().post(request, *args, **kwargs)

class TerminalUpdate(TerminalMixin, UpdateView):
    template_name = "update.html"

class TerminalDelete(TerminalMixin, DeleteMixin, View):
    pass

from django.forms import modelformset_factory
from django.urls import reverse
from django.http import HttpResponseRedirect

TerminalFormSet = modelformset_factory(Terminal, form=TerminalForm, extra=7)
from django.shortcuts import render, redirect
def create_multiple_terminals(request):
    if request.method == "POST":
        formset = TerminalFormSet(request.POST, queryset=Terminal.objects.none())
        if formset.is_valid():
            formset.save()
            # return redirect('table_list')  # Redirect to a success page
            url = reverse('org:terminal_list')  # Assuming 'table_list' is the correct URL name
            return HttpResponseRedirect(url)
    else:
        formset = TerminalFormSet(queryset=Terminal.objects.none())

    return render(request, "create_multiple_terminal.html", {"formset": formset})
    
    
# class EndDayReportList(ListView):
#     paginate_by = 5
#     def get(self, request):
#         reports = EndDayDailyReport.objects.all().order_by('-created_at')
#         return render(request, 'organization/end_day_report_list.html', {'object_list': reports})

from datetime import datetime 
class EndDayReportList(ListView):
    paginate_by = 5
    def get(self, request):
        from_date_str = request.GET.get('fromDate')
        to_date_str = request.GET.get('toDate')
        print(from_date_str)
        print(to_date_str)

        # Convert fromDate and toDate strings to datetime objects
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None
        if from_date_str and to_date_str:
            reports = []

            # pass
            for report in EndDayDailyReport.objects.all().order_by('created_at'):
                report_datetime = datetime.strptime(report.date_time, '%Y-%m-%dT%H:%M:%S.%f')
                # Check if the report_date falls within the specified range
                if from_date.date() <= report_datetime.date() <= to_date.date():
                    reports.append(report)
            
            print(reports)


        else:
            reports = EndDayDailyReport.objects.all().order_by('-created_at')
        return render(request, 'organization/end_day_report_list.html', {'object_list': reports})
