from django.urls import path

from ..views.purchaserequisition import Apisent, Apihome, Api_details,filter_date_api,filter_date_apifirst,getItemHistory,postSales,getorderdate,delorderHistory


urlpatterns = [
    path("req/", Apisent),
    path("reqget/", Apihome),
    path("reqdetails/<int:id>", Api_details),
    path("reqfilter/",filter_date_api),
    path("reqfilterfirst/",filter_date_apifirst),
    path("reqitemhistory/<int:itemid>", getItemHistory),
    path("postsales/", postSales),
    path("getorderdate/", getorderdate),
    path("deletedata/", delorderHistory),

]