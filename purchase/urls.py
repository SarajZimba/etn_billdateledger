from django.urls import path

from .views import VendorList,VendorDetail,VendorCreate,VendorUpdate,VendorDelete

urlpatterns = [
    path('vendor/', VendorList.as_view(), name='vendor_list'),
    path('vendor/<int:pk>/', VendorDetail.as_view(), name='vendor_detail'),
    path('vendor/create/', VendorCreate.as_view(), name='vendor_create'),
    path('vendor/<int:pk>/update/', VendorUpdate.as_view(), name='vendor_update'),
    path('vendor/delete', VendorDelete.as_view(), name='vendor_delete'),
]


from .views import ProductPurchaseCreateView, PurchaseListView, PurchaseDetailView, MarkPurchaseVoid, PurchaseBookListView, VendorWisePurchaseView

urlpatterns += [
    path('purchase/create/', ProductPurchaseCreateView.as_view(), name="product_purchase_create"),
    path('purchase/<int:pk>/', PurchaseDetailView.as_view(), name="purchase_detail"),
    path('purchase/void/<int:pk>', MarkPurchaseVoid.as_view(), name="purchase_void"),
    path('purchase/', PurchaseListView.as_view(), name="purchase_list"),
    path('pb/', PurchaseBookListView.as_view(), name="purchase_book_list"),
    path('vendor-wise/', VendorWisePurchaseView.as_view(), name="vendor_wise_purchase"),

]

from .views import AssetPurchaseList,AssetPurchaseDetail,AssetPurchaseCreate,AssetPurchaseUpdate#,AssetPurchaseDelete
urlpatterns += [
path('asset/', AssetPurchaseList.as_view(), name='assetpurchase_list'),
path('asset/<int:pk>/', AssetPurchaseDetail.as_view(), name='assetpurchase_detail'),
path('asset/create/', AssetPurchaseCreate.as_view(), name='assetpurchase_create'),
path('asset/<int:pk>/update/', AssetPurchaseUpdate.as_view(), name='assetpurchase_update'),
# path('asset/delete', AssetPurchaseDelete.as_view(), name='assetpurchase_delete'),
]

from .views import PurchaseEntryUploadView

urlpatterns += [
    path('upload-purchase/', PurchaseEntryUploadView.as_view(), name='upload_purchase_entry'),
]

from .views import PurchasedProducts
urlpatterns += [
    path('today-prodpur', PurchasedProducts.as_view(), name='today-prodpur')
]

from .views import ImportProductPurchaseCreateView, ImportPurchaseListView, ImportPurchaseDetailView, ImportMarkPurchaseVoid

urlpatterns += [
    path('importpur_chase/create/', ImportProductPurchaseCreateView.as_view(), name="importproduct_purchase_create"),
    path('importpur_chase/<int:pk>/', ImportPurchaseDetailView.as_view(), name="importpur_chase_detail"),
    path('importpur_chase/void/<int:pk>', ImportMarkPurchaseVoid.as_view(), name="importpur_chase_void"),
    path('importpur_chase/', ImportPurchaseListView.as_view(), name="importpur_chase_list")
]
