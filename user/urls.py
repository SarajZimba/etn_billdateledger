from django.contrib.auth.views import LoginView
from django.urls import path

from .views import (
    UserCreate,
    UserDelete,
    UserDetail,
    UserList,
    UserUpdate,
    logout_user,
)


app_name = "user"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login_view"),
    path("logout/", logout_user, name="logout"),
]


urlpatterns += [
    path("user/", UserList.as_view(), name="user_list"),
    path("user/<int:pk>/", UserDetail.as_view(), name="user_detail"),
    path("user/create/", UserCreate.as_view(), name="user_create"),
    path("user/<int:pk>/update/", UserUpdate.as_view(), name="user_update"),
    path("user/delete", UserDelete.as_view(), name="user_delete"),
]

from .views import (
    CustomerList,
    CustomerDetail,
    CustomerCreate,
    CustomerUpdate,
    CustomerDelete,
)

urlpatterns += [
    path("customer/", CustomerList.as_view(), name="customer_list"),
    path("customer/<int:pk>/", CustomerDetail.as_view(), name="customer_detail"),
    path("customer/create/", CustomerCreate.as_view(), name="customer_create"),
    path("customer/<int:pk>/update/", CustomerUpdate.as_view(), name="customer_update"),
    path("customer/delete", CustomerDelete.as_view(), name="customer_delete"),
]

from .views import (
    AgentCreate,
    AgentDelete,
    AgentList,
    AgentUpdate,
)


urlpatterns += [
    path("agent/", AgentList.as_view(), name="agent_list"),
    path("agent/create/", AgentCreate.as_view(), name="agent_create"),
    path("agent/<int:pk>/update/", AgentUpdate.as_view(), name="agent_update"),
    path("agent/delete", AgentDelete.as_view(), name="agent_delete"),
]

from .views import (
    SaleAgentCreate,
    SaleAgentDelete,
    SaleAgentList,
    SaleAgentUpdate,
)


urlpatterns += [
    path("saleman/", SaleAgentList.as_view(), name="saleman_list"),
    path("saleman/create/", SaleAgentCreate.as_view(), name="saleman_create"),
    path("saleman/<int:pk>/update/", SaleAgentUpdate.as_view(), name="saleman_update"),
    path("saleman/delete", SaleAgentDelete.as_view(), name="saleman_delete"),
]
