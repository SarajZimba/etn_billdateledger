
from django.urls import path
urlpatterns = []

from .views import ProductCategoryList,ProductCategoryDetail,ProductCategoryCreate,ProductCategoryUpdate,ProductCategoryDelete
urlpatterns += [
path('prdct/category/', ProductCategoryList.as_view(), name='product_category_list'),
path('prdct/category/<int:pk>/', ProductCategoryDetail.as_view(), name='product_category_detail'),
path('prdct/category/create/', ProductCategoryCreate.as_view(), name='product_category_create'),
path('prdct/category/<int:pk>/update/', ProductCategoryUpdate.as_view(), name='product_category_update'),
path('prdct/category/delete', ProductCategoryDelete.as_view(), name='product_category_delete'),
]
               
from .views import ProductList,ProductDetail,ProductCreate,ProductUpdate,ProductDelete, ProductUpload
urlpatterns += [
path('product/', ProductList.as_view(), name='product_list'),
path('product/<int:pk>/', ProductDetail.as_view(), name='product_detail'),
path('product/create/', ProductCreate.as_view(), name='product_create'),
path('product/<int:pk>/update/', ProductUpdate.as_view(), name='product_update'),
path('product/delete', ProductDelete.as_view(), name='product_delete'),
path('product/upload/', ProductUpload.as_view(), name='product_upload'),

]
               
from .views import CustomerProductList,CustomerProductDetail,CustomerProductCreate,CustomerProductUpdate,CustomerProductDelete
urlpatterns += [
path('prdct/client/', CustomerProductList.as_view(), name='customerproduct_list'),
path('prdct/client/<int:pk>/', CustomerProductDetail.as_view(), name='customerproduct_detail'),
path('prdct/client/create/', CustomerProductCreate.as_view(), name='customerproduct_create'),
path('prdct/client/<int:pk>/update/', CustomerProductUpdate.as_view(), name='customerproduct_update'),
path('prdct/client/delete', CustomerProductDelete.as_view(), name='customerproduct_delete'),
]

               
from .views import ProductStockList,ProductStockDetail,ProductStockCreate,ProductStockUpdate,ProductStockDelete
urlpatterns += [
path('stock/', ProductStockList.as_view(), name='productstock_list'),
path('stock/<int:pk>/', ProductStockDetail.as_view(), name='productstock_detail'),
path('stock/create/', ProductStockCreate.as_view(), name='productstock_create'),
path('stock/<int:pk>/update/', ProductStockUpdate.as_view(), name='productstock_update'),
path('stock/delete', ProductStockDelete.as_view(), name='productstock_delete'),
]

from .views import BranchStockList,BranchStockDetail,BranchStockCreate,BranchStockUpdate,BranchStockDelete, ReconcileView, BranchStockUploadView, UpdateDateForReconcilationView, BranchStockTotalList
urlpatterns += [
path('bstck/', BranchStockList.as_view(), name='branchstock_list'),
path('bstcktotal/', BranchStockTotalList.as_view(), name='branchstock_total'),
path('bstck/<int:pk>/', BranchStockDetail.as_view(), name='branchstock_detail'),
path('bstck/create/', BranchStockCreate.as_view(), name='branchstock_create'),
path('bstck/<int:pk>/update/', BranchStockUpdate.as_view(), name='branchstock_update'),
path('bstck/delete', BranchStockDelete.as_view(), name='branchstock_delete'),
path('reconcile/', ReconcileView.as_view(), name='reconcile'),
path('bstck/upload-opening/', BranchStockUploadView.as_view(), name='branchstock_upload'),
path('update-date-reconcilation/', UpdateDateForReconcilationView.as_view(), name='update_date_reconcilation'),


]


from .views import RequisitionBranchStockList,RequisitionBranchStockDetail,RequisitionBranchStockCreate,RequisitionBranchStockUpdate,RequisitionBranchStockDelete
urlpatterns += [
path('bstck/', RequisitionBranchStockList.as_view(), name='branchstock_list'),
path('bstck/<int:pk>/', RequisitionBranchStockDetail.as_view(), name='branchstock_detail'),
path('bstck/create/', RequisitionBranchStockCreate.as_view(), name='branchstock_create'),
path('bstck/<int:pk>/update/', RequisitionBranchStockUpdate.as_view(), name='branchstock_update'),
path('bstck/delete', RequisitionBranchStockDelete.as_view(), name='branchstock_delete')


]
   