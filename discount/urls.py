from django.urls import path

from .views import DiscountTableList,DiscountTableDetail,DiscountTableCreate,DiscountTableUpdate,DiscountTableDelete

urlpatterns = [
    path('discount/', DiscountTableList.as_view(), name='discounttable_list'),
    path('discount/<int:pk>/', DiscountTableDetail.as_view(), name='discounttable_detail'),
    path('discount/create/', DiscountTableCreate.as_view(), name='discounttable_create'),
    path('discount/<int:pk>/update/', DiscountTableUpdate.as_view(), name='discounttable_update'),
    path('discount/delete', DiscountTableDelete.as_view(), name='discounttable_delete'),
]
    