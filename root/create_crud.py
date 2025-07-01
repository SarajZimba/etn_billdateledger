import os


class AutoCrud:
    model = None
    view_file = "views.py"
    url_file = "urls.py"
    form_file = "forms.py"

    def __init__(self, model):
        self.model = model
        self.create_form_class()
        self.create_views()
        self.create_urls()
        self.create_templates()

    def create_form_class(self):
        new = True
        if os.path.isfile(self.form_file):
            new = False
            form_file = open(self.form_file, "a+")
        else:
            form_file = open(self.form_file, "w+")

        if new:
            form_file.write(
                """
from django import forms
from django.forms.models import inlineformset_factory
from root.forms import BaseForm # optional
        """
            )
        form_file.write(
            f"""
from .models import {self.model}

class {self.model}Form(BaseForm, forms.ModelForm):
    class Meta:
        model = {self.model}
        fields = '__all__'
        exclude = ['is_deleted', 'status', 'deleted_at',]
                        """
        )
        form_file.close()

    def create_views(self):
        new = True
        if os.path.isfile(self.view_file):
            new = False
            view_file = open(self.view_file, "a+")
        else:
            view_file = open(self.view_file, "w+")

        if new:
            view_file.write(
                f"""
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView,DetailView,ListView,TemplateView,UpdateView,View
from root.utils import DeleteMixin
from .models import {self.model}
from .forms import {self.model}Form
"""
            )

        view_file.write(
            f"""
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView,DetailView,ListView,TemplateView,UpdateView,View
from root.utils import DeleteMixin
from .models import {self.model}
from .forms import {self.model}Form
class {self.model}Mixin:
    model = {self.model}
    form_class = {self.model}Form
    paginate_by = 10
    queryset = {self.model}.objects.filter(status=True,is_deleted=False)
    success_url = reverse_lazy('{self.model.lower()}_list')

class {self.model}List({self.model}Mixin, ListView):
    template_name = "{self.model.lower()}/{self.model.lower()}_list.html"
    queryset = {self.model}.objects.filter(status=True,is_deleted=False)

class {self.model}Detail({self.model}Mixin, DetailView):
    template_name = "{self.model.lower()}/{self.model.lower()}_detail.html"

class {self.model}Create({self.model}Mixin, CreateView):
    template_name = "create.html"

class {self.model}Update({self.model}Mixin, UpdateView):
    template_name = "update.html"

class {self.model}Delete({self.model}Mixin, DeleteMixin, View):
    pass
"""
        )

    def create_urls(self):
        new = True
        if os.path.isfile(self.url_file):
            new = False
            url_file = open(self.url_file, "a+")
        else:
            url_file = open(self.url_file, "w+")

        if new:
            url_file.write(
                """
from django.urls import path
urlpatterns = []
"""
            )
        url_file.write(
            f"""
from .views import {self.model}List,{self.model}Detail,{self.model}Create,{self.model}Update,{self.model}Delete
urlpatterns += [
path('{self.model.lower()}/', {self.model}List.as_view(), name='{self.model.lower()}_list'),
path('{self.model.lower()}/<int:pk>/', {self.model}Detail.as_view(), name='{self.model.lower()}_detail'),
path('{self.model.lower()}/create/', {self.model}Create.as_view(), name='{self.model.lower()}_create'),
path('{self.model.lower()}/<int:pk>/update/', {self.model}Update.as_view(), name='{self.model.lower()}_update'),
path('{self.model.lower()}/delete', {self.model}Delete.as_view(), name='{self.model.lower()}_delete'),
]
               """
        )
        url_file.close()

    def create_templates(self):
        pass

        new = True
        # templates/blogcategory
        if not os.path.exists(f"../templates/{self.model.lower()}"):
            os.makedirs(f"../templates/{self.model.lower()}")
        if os.path.isfile(
            f"../templates/{self.model.lower()}/{self.model.lower()}_list.html"
        ):
            new = False
            view_file = open(
                f"../templates/{self.model.lower()}/{self.model.lower()}_list.html",
                "a+",
            )
        else:
            view_file = open(
                f"../templates/{self.model.lower()}/{self.model.lower()}_list.html",
                "w+",
            )

        if new:
            view_file.write(
                """
{%extends 'base.html'%}
{% block pagetitle %}"""
                + self.model
                + " List {% endblock %}\n"
                + "{% block home %} {% url '"
                + self.model.lower()
                + "_list' %} {% endblock %}\n"
                + "{% block title %}"
                + self.model
                + " List {% endblock %}\n"
                + "{% block content %}\n {% include 'components/title_bar.html' with title=' "
                + self.model
                + " List ' create='/create/'  %}"
                + """
                <div class="card">\n
                {% include 'components/search_filter.html' with """
                + f""" search_title="Search {self.model}" create_url="{self.model.lower()}_create" create_button="Add {self.model}" """
                + """%} \n"""
                + """

    <div class="card-body pt-0">
    <!--begin::Table-->
    <div id="kt_customers_table_wrapper" class="dataTables_wrapper dt-bootstrap4 no-footer">
      <div class="table-responsive">
        <table class="table align-middle table-row-dashed fs-6 gy-5 dataTable no-footer" id="kt_customers_table">
          <!--begin::Table head-->
          {%if object_list%}
          <thead>
            <!--begin::Table row-->
            <tr class="text-start text-gray-400 fw-bolder fs-7 text-uppercase gs-0">
              <th class="w-10px pe-2 sorting_disabled" rowspan="1" colspan="1" aria-label="" style="width: 29.25px;">
                <div class="form-check form-check-sm form-check-custom form-check-solid me-3">
                  <input class="form-check-input" type="checkbox" data-kt-check="true"
                    data-kt-check-target="#kt_customers_table .form-check-input" value="1">
                </div>
              </th>
              <th class="min-w-125px sorting" tabindex="0" > Header Name</th>
              <th class="min-w-125px sorting" tabindex="0" > Header Name</th>
              <th class="min-w-125px sorting" tabindex="0" > Header Name</th>
              <th class="min-w-125px sorting" tabindex="0" > Status</th>
              <th class="min-w-125px sorting" tabindex="0" > Header Name</th>

              <th class="text-end min-w-70px sorting_disabled" rowspan="1" colspan="1" aria-label="Actions"
                style="width: 125.287px;">Actions</th>
            </tr>
            <!--end::Table row-->
          </thead>
          {%endif%}
          <tbody class="fw-bold text-gray-600">

          {% for object in object_list %}
             <tr class="odd" id="obj-{{object.pk}}">
                <td>
                    <div class="form-check form-check-sm form-check-custom form-check-solid">
                    <input class="form-check-input" type="checkbox" value="1">
                    </div>
                </td>

                <td>value 1</td>
                <td>value 2</td>
                <td>value 3</td>
                <td>{% include 'components/status.html' with status=object.status%}</td>
                <td>value 4</td>
                <td class="text-end">
                <a href="#" class="btn btn-sm btn-light btn-active-light-primary" data-kt-menu-trigger="click"
                                data-kt-menu-placement="bottom-end">Actions
                                <!--begin::Svg Icon | path: icons/duotune/arrows/arr072.svg-->
                                <span class="svg-icon svg-icon-5 m-0">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                                    <path
                                        d="M11.4343 12.7344L7.25 8.55005C6.83579 8.13583 6.16421 8.13584 5.75 8.55005C5.33579 8.96426 5.33579 9.63583 5.75 10.05L11.2929 15.5929C11.6834 15.9835 12.3166 15.9835 12.7071 15.5929L18.25 10.05C18.6642 9.63584 18.6642 8.96426 18.25 8.55005C17.8358 8.13584 17.1642 8.13584 16.75 8.55005L12.5657 12.7344C12.2533 13.0468 11.7467 13.0468 11.4343 12.7344Z"
                                        fill="black"></path>
                                    </svg>
                                </span>
                                <!--end::Svg Icon-->
                                </a>
                                <!--begin::Menu-->
                                <div
                                class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-600 menu-state-bg-light-primary fw-bold fs-7 w-125px py-4"
                                data-kt-menu="true" style="">
                                <!--begin::Menu item-->
                                <!--end::Menu item-->
                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="{% url '"""
                + self.model.lower()
                + """_update' object.pk %}" class="menu-link px-3"
                                    data-kt-customer-table-filter="update_row">Update</a>
                                </div>
                                <div class="menu-item px-3">
                                    <a onclick="remove({{object.pk}},'{% url " """
                + f"""{self.model.lower()}_delete"""
                + """" %}','{{object}}',)" class="menu-link px-3" id="obj"
                                    data-kt-customer-table-filter="delete_row">Delete</a>
                                </div>
'
                  <!--end::Menu item-->
                </div>
                </td>
             </tr>
             {%empty%}
             {% include 'components/empty.html' with """
                + f''' title="{self.model}"'''
                + """%}
              {% endfor %}

          </tbody>
          <!--end::Table body-->
        </table>
      </div>
    {%if object_list%}
      {% include 'pagination.html' %}
    {%endif%}
    </div>
    <!--end::Table-->
  </div>
  <!--end::Card body-->
</div>

<script>
</script>

{% endblock %}

"""
            )


def main():
    model_name = input("Enter model name \n[separate with commas for multiple] :")
    model_list = model_name.split(",")

    for model in model_list:
        AutoCrud(model)
        print(f"Created {model}")


if __name__ == "__main__":
    main()
