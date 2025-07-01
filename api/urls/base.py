from .user import urlpatterns as user_urlpatterns
from .product import urlpatterns as product_urlpatterns
from .bill import urlpatterns as bill_urlpatterns
from .organization import urlpatterns as org_urlpatterns
from .discount_urls import urlpatterns as discount_urlspatterns
from .purchaserequisition_api import urlpatterns as purchaserequisition_urlpattern
from .accounting_urls import urlpatterns as accounting_urlpatterns
from .mobilepayment_type import urlpatterns as mobile_urlpatterns
from .endday_report import urlpatterns as enddayreport_urlpatterns
from .today_report import urlpatterns as todayreport_urlpatterns
from .category_wise_report import urlpatterns as category_wise_sale_urlpatterns
from .report import urlpatterns as report_urlpatterns 
from.master import urlpatterns as master_urlpatterns
from .bill_todayid import urlpatterns as bill_todayid_urlpatterns

urlpatterns = (
    [] + user_urlpatterns + product_urlpatterns + bill_urlpatterns + org_urlpatterns+discount_urlspatterns+purchaserequisition_urlpattern+accounting_urlpatterns+mobile_urlpatterns+enddayreport_urlpatterns+todayreport_urlpatterns+category_wise_sale_urlpatterns +report_urlpatterns+ master_urlpatterns+ bill_todayid_urlpatterns
)
