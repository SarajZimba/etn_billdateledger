from django.urls import path
from api.views.organization import OrganizationApi, BranchApi, PrinterSettingListView,TestMaster
from rest_framework import routers

router = routers.DefaultRouter()

router.register("organization", OrganizationApi)
router.register("branch", BranchApi)

urlpatterns = [
    path('printer-setting/<int:branch_id>/<int:terminal_no>', PrinterSettingListView.as_view(), name='printer-setting'),
    path('test-master', TestMaster.as_view(), name='test-master'),
    ] + router.urls

from django.urls import path
from api.views.organization import TrialBalanceToggleAPIView

urlpatterns += [
    path('trialbalance/toggle/', TrialBalanceToggleAPIView.as_view(), name='trialbalance-toggle'),
]