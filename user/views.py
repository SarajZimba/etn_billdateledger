from django.contrib.auth import get_user_model, logout
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.urls import reverse_lazy
import requests
import environ
env = environ.Env(DEBUG=(bool, False))

from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from root.utils import DeleteMixin, remove_from_DB
from user.permission import IsAdminMixin, AdminBillingMixin

from .forms import UserCreateForm, UserForm, AdminForm


User = get_user_model()


class UserMixin(IsAdminMixin):
    model = User
    form_class = UserCreateForm
    paginate_by = 50
    queryset = User.objects.filter(status=True)
    success_url = reverse_lazy("user:user_list")
    search_lookup_fields = ["username", "email", "full_name"]


class UserList(UserMixin, ListView):
    template_name = "user/user_list.html"
    queryset = User.objects.filter(status=True, is_deleted=False, groups__name__in=["admin"])

    def get_queryset(self, *args, **kwargs):
        queryset = self.queryset.exclude(id=self.request.user.id)
        return queryset


class UserDetail(UserMixin, DetailView):
    template_name = "user/user_detail.html"


class UserCreate(UserMixin, CreateView):
    template_name = "create.html"

    def form_valid(self, form):
        form.instance.is_superuser = False
        form.instance.is_staff = True
        form.instance.organization = self.request.user.organization
        object = form.save()
        # FLASK_URL = env("FLASK_USER_CREATE_URL")
        # TOKEN = env("FLASK_USER_CREATE_KEY")
        # data= {
        #     "token":TOKEN,
        #     "username": object.username,
        #     "baseURL":self.request.scheme+'://'+self.request.get_host()
        # }
        # requests.post(
        #     FLASK_URL,
        #     json=data
        # )
        group, _ = Group.objects.get_or_create(name='admin')
        object.groups.add(group)
        return super().form_valid(form)
        


class UserAdmin(UserMixin, CreateView):
    template_name = "create.html"


class UserUpdate(UserMixin, UpdateView):
    template_name = "update.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        old_username = self.object.username
        p = super().post(request, *args, **kwargs)
        # FLASK_URL = env("FLASK_USER_UPDATE_URL")
        # TOKEN = env("FLASK_USER_CREATE_KEY")
        # data= {
        #     "token":TOKEN,
        #     "username":old_username,
        #     "newUsername": request.POST.get('username'),
        #     "baseURL":request.scheme+'://'+request.get_host(),
        #     "type":"UPDATE"
        # }
        # response = requests.post(
        #     FLASK_URL,
        #     json=data
        # )
        return p
        


class UserDelete(UserMixin, View):
    def get(self, request):
        status = remove_from_DB(self, request)
        return JsonResponse({"deleted": status})


def logout_user(request):
    logout(request)
    return redirect(reverse_lazy("user:login_view"))


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
from .models import Customer
from .forms import CustomerForm


class CustomerMixin(AdminBillingMixin):
    model = Customer
    form_class = CustomerForm
    paginate_by = 50
    queryset = Customer.objects.filter(status=True, is_deleted=False)
    success_url = reverse_lazy("user:customer_list")
    search_lookup_fields = ["name", "tax_number", "contact_number", "email"]


class CustomerList(CustomerMixin, ListView):
    template_name = "customer/customer_list.html"
    queryset = Customer.objects.active()


class CustomerDetail(CustomerMixin, DetailView):
    template_name = "customer/customer_detail.html"


class CustomerCreate(CustomerMixin, CreateView):
    template_name = "create.html"


class CustomerUpdate(CustomerMixin, UpdateView):
    template_name = "update.html"


class CustomerDelete(CustomerMixin, DeleteMixin, View):
    pass


class AgentMixin(IsAdminMixin):
    model = User
    form_class = UserForm
    paginate_by = 50
    queryset = User.objects.filter(status=True, is_deleted=False)
    success_url = reverse_lazy("user:agent_list")
    search_lookup_fields = ["username", "email", "full_name"]


class AgentList(AgentMixin, ListView):
    template_name = "agent/agent_list.html"
    queryset = User.objects.filter(
        groups__name__in=["agent"], status=True, is_deleted=False
    )


class AgentCreate(AgentMixin, CreateView):
    template_name = "create.html"

    def form_valid(self, form):

        form.instance.is_superuser = False
        form.instance.is_staff = True
        object = form.save()

        group, created = Group.objects.get_or_create(name="agent")
        object.groups.add(group)
        return super().form_valid(form)


class AgentUpdate(AgentMixin, UpdateView):
    template_name = "update.html"


class AgentDelete(AgentMixin, DeleteMixin, View):
    pass

class SaleAgentMixin(IsAdminMixin):
    model = User
    form_class = UserForm
    paginate_by = 50
    queryset = User.objects.filter(status=True, is_deleted=False)
    success_url = reverse_lazy("user:saleman_list")
    search_lookup_fields = ["username", "email", "full_name"]


class SaleAgentList(SaleAgentMixin, ListView):
    template_name = "saleman/saleman_list.html"
    queryset = User.objects.filter(
        groups__name__in=["billing_group"], status=True, is_deleted=False
    )


class SaleAgentCreate(SaleAgentMixin, CreateView):
    template_name = "create.html"

    def form_valid(self, form):

        form.instance.is_superuser = False
        form.instance.is_staff = True
        object = form.save()

        group, created = Group.objects.get_or_create(name="billing_group")
        object.groups.add(group)
        return super().form_valid(form)


class SaleAgentUpdate(SaleAgentMixin, UpdateView):
    template_name = "update.html"


class SaleAgentDelete(SaleAgentMixin, DeleteMixin, View):
    pass