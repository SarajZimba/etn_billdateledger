from django.urls import reverse_lazy
from django.views.generic import CreateView,DetailView,ListView,UpdateView,View
from root.utils import DeleteMixin
from .models import DiscountTable
from .forms import DiscountTableForm


from django.urls import reverse_lazy
from django.views.generic import CreateView,DetailView,ListView,UpdateView,View
from root.utils import DeleteMixin
from .models import DiscountTable
from .forms import DiscountTableForm

class DiscountTableMixin:
    model = DiscountTable
    form_class = DiscountTableForm
    paginate_by = 10
    queryset = DiscountTable.objects.filter(status=True,is_deleted=False)
    success_url = reverse_lazy('discounttable_list')

class DiscountTableList(DiscountTableMixin, ListView):
    template_name = "discounttable/discounttable_list.html"
    queryset = DiscountTable.objects.filter(status=True,is_deleted=False)

class DiscountTableDetail(DiscountTableMixin, DetailView):
    template_name = "discounttable/discounttable_detail.html"

class DiscountTableCreate(DiscountTableMixin, CreateView):
    template_name = "discounttable/discounttable_create.html"

class DiscountTableUpdate(DiscountTableMixin, UpdateView):
    template_name = "update.html"

class DiscountTableDelete(DiscountTableMixin, DeleteMixin, View):
    pass
