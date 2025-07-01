from api.views.product import CustomerProductAPI, ProductList, ProductDetail,ProductMultipriceapi, bulk_product_requisition, ApiItemReconcilationView, CheckAllowReconcilationView,\
 ProductCreateAPIView, ProductUpdateAPIView, ProductDeleteAPIView, CategoryAPIView, ProductWithBranchStockList, BranchWiseProduct
from django.urls import path

from rest_framework import routers

router = routers.DefaultRouter()
router.register("customer-product-list", CustomerProductAPI)

urlpatterns = [
    # path("product-list/", ProductList.as_view(), name="api_product_list"),
    path("product-list/", ProductList.as_view({'get':'list'}), name="api_branch_product_list"),
    path("all-product-list/", ProductWithBranchStockList.as_view({'get':'list'}), name="api_all_product_list"),
    # path("product-list/", ProductList.as_view({'get':'list'}), name="api_product_list"),
    path("product-detail/<int:pk>", ProductDetail.as_view(), name="api_product_detail"), 
    path("product-prices/", ProductMultipriceapi.as_view(), name="api_product_price"),
    path("bulk-requisition/", bulk_product_requisition, name="api_bulk_product_requisition"),
    path("bulk-product-reconcilation/", ApiItemReconcilationView.as_view(), name="api_bulk_product_reconcile"),
    path("check-reconcilation/", CheckAllowReconcilationView.as_view(), name="api_check_reconcilation"),
    path("product-create/", ProductCreateAPIView.as_view(), name="product-create"),
    path('product-update/<int:pk>/', ProductUpdateAPIView.as_view(), name='product-update'),
    path('product-delete/<int:pk>/', ProductDeleteAPIView.as_view(), name='product-delete'),

    path("product-categories", CategoryAPIView.as_view(), name="product-categories"),
    path("product-branchwise/<int:branch>", BranchWiseProduct.as_view({'get':'list'}), name="branchwise-product")



] + router.urls
 
