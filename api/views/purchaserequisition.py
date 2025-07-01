from pathlib import Path
import os
import environ
from django.conf import settings
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(settings.BASE_DIR, ".env"))



from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
import json
import mysql.connector
from rest_framework import status, response

mydb = mysql.connector.connect(
    host="localhost", user=env('DB_USERNAME'), password=env('DB_PASSWORD'), database=env('DB_NAME')
)


print("connected ...")


def dicfetchall(cursor):
    try:
        desc = cursor.description
    except Exception as e:
        pass
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]


def firsttable():
    mycursor = mydb.cursor()
    sql = "SELECT * FROM intbl_purchaserequisition "
    try:
        mycursor.execute(sql)
        r = dicfetchall(mycursor)
    except Exception as e:
        print(e)
        
    return r


def secondtable(id):
    mycursor = mydb.cursor()
    sql2 = f"""
      select * from intbl_purchaserequisition_contract where PurchaseReqID={id} ORDER BY ItemID DESC;
    """
    try:
        mycursor.execute(sql2)
        data = dicfetchall(mycursor)
    except Exception as e:
        print(e)

    return data


def getLastpurchaseidata(data, id):
    query = []
    for item in data:
        sql = f"""SELECT Rate as last_purchase FROM `intbl_purchaserequisition_contract` WHERE ItemID ={item['ItemID']} and PurchaseReqID != {id} order by PurchaseReqID desc limit 1;"""
        query.append(sql)
    return query


def fetchData(data2):
    _list = []
    for items in data2:
        mycursor = mydb.cursor()
        mycursor.execute(items)
        data = dicfetchall(mycursor)
        _list.append(data)

    return _list


def convertToDictnory(data):
    _data = []
    for i in range(0, len(data)):
        if len(data[i]) == 0:
            _data.append({"last_purchase": 0})
        else:
            _data.append(data[i][0])

    return _data


def addDatatoDict(dicdata=0, data=0):
    _data = []
    for i in range(len(data)):
        if len(dicdata[i]) != 0:
            temp = data[i]
            temp1 = dicdata[i]
            key = temp1.keys()
            value = temp1.values()
            a = list(key)
            b = list(value)
            temp[a[0]] = float(b[0])
            _data.append(temp)
        else:
            _data.append(data[i])
    return _data


# Create your views here.
@api_view(["GET"])
def Apihome(request):
    data = firsttable()

    if len(data) == 0:
        return JsonResponse({"msg": "all item is empty", "status": status.HTTP_200_OK})
    return JsonResponse({"purchaserequisition": data})


@api_view(["GET"])
def Api_details(request, id):
    data = secondtable(id)
    data2 = getLastpurchaseidata(data, id)
    lastpurchase = fetchData(data2)
    normalize = convertToDictnory(lastpurchase)
    data = addDatatoDict(normalize, data)

    return JsonResponse(
        {"intbl_purchaserequisition_contract": data, "status": status.HTTP_200_OK}
    )


@api_view(["GET"])
def filter_date_api(request):
    time = request.GET["time"] or ""
    time2 = request.GET["time2"] or ""
    company_name = request.GET["company_name"] or ""
    mycursor = mydb.cursor()
    sql = f"SELECT * FROM intbl_purchaserequisition WHERE ReceivedDate BETWEEN '{time}' AND '{time2}' and Company_Name like '%{company_name}%' ORDER BY `IDIntbl_PurchaseRequisition` DESC ;"

    mycursor.execute(sql)
    data = dicfetchall(mycursor)
    return JsonResponse({"purchaserequisition": data, "status": status.HTTP_200_OK})
    
    
@api_view(["GET"])
def filter_date_apifirst(request):
    time = request.GET.get("firsttime", "")
    time2 = request.GET.get("secondtime", "")
    outletname = request.GET.get("outlet_name", "")
    outletname.replace('%20',' ')
    mycursor = mydb.cursor()
    sql = f"SELECT * FROM intbl_purchaserequisition WHERE ReceivedDate BETWEEN '{time}' AND '{time2}' and Outlet_Name='{outletname}'ORDER BY `IDIntbl_PurchaseRequisition` DESC ;"
    mycursor.execute(sql)
    data = dicfetchall(mycursor)
    return JsonResponse({"purchaserequisition": data, "status": status.HTTP_200_OK})

@api_view(["GET"])
def getItemHistory(request,itemid):
    outletname = request.GET.get("outlet_name", "")
    limit = request.GET.get("limit", 10)
    mycursor=mydb.cursor()
    sql = f"select a.rate, a.UnitsOrdered, b.ReceivedDate from intbl_purchaserequisition_contract a, intbl_purchaserequisition b where a.PurchaseReqID = b.IDIntbl_PurchaseRequisition and b.Outlet_Name='{outletname}' and a.ItemID = {itemid} order by a.PurchaseReqID desc limit {limit}"
    mycursor.execute(sql)
    data=dicfetchall(mycursor)
    return JsonResponse({"intbl_purchaserequisition_contract":data})


@api_view(["POST"])
def Apisent(request):

    mycursor = mydb.cursor()
    body = request.body
    data = {}
    data = json.loads(body)

    # print(data)
    sql = f"""                                    
        INSERT INTO `intbl_purchaserequisition`
        (IDIntbl_PurchaseRequisition,RequisitionType,Date,TotalAmount,TaxAmount,Company_Name,State,ReceivedDate,purchaseBillNumber,DiscountAmount,Outlet_Name)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

    sql2 = f"""
        INSERT INTO `intbl_purchaserequisition_contract`
        (ItemID,UnitsOrdered,PurchaseReqID,Rate,Name,BrandName,Code,UOM,StockType,Department,GroupName,ExpDate,Status,Taxable)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    # VALUES ();
    try:

        mycursor.execute(
            sql,
            (
                data["PurchaseRequistionID"],
                data["RequisitionType"],
                data["Date"],
                data["TotalAmount"],
                data["TaxAmount"],
                data["Company_Name"],
                data["State"],
                data["ReceivedDate"],
                data["purchaseBillNumber"],
                data["DiscountAmount"],
                data["Outlet_Name"],
            ),
        )

        for data in data["RequisitionDetailsList"]:

            listdata = (
                data["ItemID"],
                data["UnitsOrdered"],
                data["PurchaseReqID"],
                data["Rate"],
                data["Name"],
                data["BrandName"],
                data["Code"],
                data["UOM"],
                data["StockType"],
                data["Department"],
                data["GroupName"],
                data["ExpDate"],
                data["Status"],
                data["Taxable"],
            )
            try:
                mycursor.execute(sql2, listdata)
            except Exception as e:
                print(e)

        mydb.commit()

        print("connection closed .....")

    except Exception as e:
        print(e)
    return JsonResponse(data)
    
    
    
    
@api_view(["POST"])
def postSales(request):
    mycursor = mydb.cursor()
    body = json.dumps(request.data)
    data = json.loads(body)
    print(data)

    sql = f"""
     INSERT INTO `tblorderhistory`(Outlet_OrderID,Employee,Table_No,NoOfGuests,Start_Time,End_Time,State,Type,Discounts,Date,bill_no,Total,serviceCharge,VAT,DiscountAmt,PaymentMode,fiscal_year,GuestName,Outlet_Name)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

    """

    sql2 = f"""
      INSERT INTO tblorder_detailshistory (order_ID,ItemName,itemRate,Total,ItemType,Description,discountExempt,count)
VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
    """

    mycursor.execute(
        sql,
        (
            data["OrderID"],
            data["Employee"],
            data["TableNo"],
            data["noofGuest"],
            data["start_Time"],
            data["end_Time"],
            data["state"],
            data["type"],
            data["discounts"],
            data["date"],
            data["bill_No"],
            data["Total"],
            data["serviceCharge"],
            data["VAT"],
            data["discountAmt"],
            data["paymentMode"],
            data["fiscal_Year"],
            data["GuestName"],
            data["Outlet_Name"],
        ),
    )
    mydb.commit()

    mycursor.execute(
        f"SELECT idtblorderhistory FROM `tblorderhistory` order by idtblorderhistory desc limit 1;"
    )
    id = mycursor.fetchall()

    print("send .. ")

    for data in data["ItemDetailsList"]:
        data["orderID"] = id[0][0]
        print(data["orderID"])
        listdata = (
            data["orderID"],
            data["itemName"],
            data["ItemRate"],
            data["total"],
            data["ItemType"],
            data["Description"],
            data["disExempt"],
            data["count"],
        )
        try:
            mycursor.execute(sql2, listdata)
        except Exception as e:
            print(e)
    mydb.commit()

    return JsonResponse({"sucess": "created"})


@api_view(["GET"])
def getorderdate(request):
    mycursor = mydb.cursor()
    fdate = request.GET["fdate"] or ""
    ldate = request.GET["ldate"] or ""
    sql = f"SELECT * FROM tblorderhistory WHERE Date BETWEEN '{fdate}' AND '{ldate}'  ORDER BY `idtblorderHistory` DESC ;"
    print(sql)
    mycursor.execute(sql)
    data=dicfetchall(mycursor)
    
    return JsonResponse({"ordertable": data})
    
    
    


def getoutletid(id, date):
    mycursor = mydb.cursor()
    sql = f"SELECT `idtblorderHistory`as order_id FROM `tblorderhistory` WHERE `Outlet_OrderID`={id} and `Date` ='{date}' "
    mycursor.execute(sql)
    data = dicfetchall(mycursor)
    return data


@api_view(["POST"])
def delorderHistory(request):
    mycursor = mydb.cursor()
    outlet_id = request.data["outlet_orderID"]
    date = request.data["date"]
    order_id = getoutletid(outlet_id, date)
    
    sql = f"delete from `tblorder_detailshistory` WHERE order_ID = order_id['order_id'];"
    sql2 = f"delete from `tblorderhistory` WHERE `idtblorderHistory` = order_id['order_id'];"
    try:

        mycursor.execute(sql)
        mycursor.execute(sql2)
        mydb.commit()
    except Exception as e:
        return JsonResponse({"error": e})
    
    return JsonResponse({"msg": "hellow"})

