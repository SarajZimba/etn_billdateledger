from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError

from api.serializers.bill import (
    BillDetailSerializer,
    BillItemSerializer,
    PaymentTypeSerializer,
    BillSerializer,
    TablReturnEntrySerializer,
    TblSalesEntrySerializer,
    TblTaxEntrySerializer,
    TblTaxEntryVoidSerializer
)
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response


from bill.models import Bill, PaymentType, TablReturnEntry, TblSalesEntry, TblTaxEntry, ConflictBillNumber
from organization.models import Branch, Organization

class PaymentTypeList(ListAPIView):
    serializer_class = PaymentTypeSerializer
    queryset = PaymentType.objects.active()


class BillInfo(APIView):
    def get(self, request):
        branch_code = self.request.query_params.get("branch_code")
        terminal = self.request.query_params.get("terminal")
        branch_and_terminal = f"{branch_code}-{terminal}"
        if not branch_code or not terminal:
            return Response({"result": "Please enter branch code and terminal"},400)
        branch = get_object_or_404(Branch, branch_code=branch_code)
        current_fiscal_year = Organization.objects.last().current_fiscal_year
        last_bill_number = Bill.objects.filter(terminal=terminal, fiscal_year = current_fiscal_year, branch=branch).order_by('-bill_count_number').first()
        if last_bill_number:
            return Response({"result": last_bill_number.invoice_number})
        return Response({"result": 0})



class BillAPI(ModelViewSet):
    serializer_class = BillSerializer
    queryset = Bill.objects.active()

    def get_queryset(self, *args, **kwargs):
        queryset = Bill.objects.filter(
            is_deleted=False, status=True, agent=self.request.user
        )
        return queryset

    def get_serializer_class(self):
        detail_actions = ["retrieve", "list"]
        if self.action in detail_actions:
            return BillDetailSerializer
        return super().get_serializer_class()


class TblTaxEntryAPI(ModelViewSet):
    pagination_class = None
    serializer_class = TblTaxEntrySerializer
    queryset = TblTaxEntry.objects.all()


class TblTaxEntryUpdateView(APIView):
    
    def patch(self, request, bill_no):
        serializer = TblTaxEntryVoidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trans_date = serializer.validated_data.get('trans_date')
        org = Organization.objects.first()
        fiscal_year = org.current_fiscal_year
        try:
            bill_date = trans_date[:10]
            bill_date = datetime.strptime(bill_date, "%Y-%m-%d").date()
        except Exception:
            return Response({'message':'Date time format incorrect'}, status=400)
            

        instance = TblTaxEntry.objects.filter(bill_no=bill_no, bill_date=bill_date)

        if not instance:
            return Response({'message':'No data available with provided details'}, status=404)
        instance = instance.first()

        is_active_data = serializer.validated_data.get("is_active")
        reason = serializer.validated_data.get("reason")


        if is_active_data == "no": 
            miti = ""
            quantity = 1
            try:
                # obj = TblSalesEntry.objects.get(bill_no=instance.bill_no, customer_pan=instance.customer_pan )

                obj = Bill.objects.get(
                    invoice_number=instance.bill_no,
                    customer_tax_number=instance.customer_pan,
                    fiscal_year=fiscal_year
                )
                obj.status = False
                obj.save()
                
                miti = obj.transaction_miti
                quantity = obj.bill_items.count()

                return_entry = TablReturnEntry(
                    bill_date=instance.bill_date,
                    bill_no=instance.bill_no,
                    customer_name=instance.customer_name,
                    customer_pan=instance.customer_pan,
                    amount=instance.amount,
                    NoTaxSales=0,
                    ZeroTaxSales=0,
                    taxable_amount=instance.taxable_amount,
                    tax_amount=instance.tax_amount,
                    miti=miti,
                    ServicedItem="Goods",
                    quantity=quantity,
                    reason=reason,
                )
                return_entry.save()

            except:
                return Response({'message':'Something Went Wrong'}, status=500)
        instance.save()


        return Response({'message':'Successful'})



class TblSalesEntryAPI(ModelViewSet):
    serializer_class = TblSalesEntrySerializer
    queryset = TblSalesEntry.objects.all()


class TablReturnEntryAPI(ModelViewSet):
    serializer_class = TablReturnEntrySerializer
    queryset = TablReturnEntry.objects.all()

class BulkBillCreateView(APIView):

    def post(self, request):
        bills = request.data.get('bills', [])
        if not bills:
            return Response({'details':"Bills is required"}, status=400)
        conflict_invoices = []
        for bill in bills:
            serializer = BillSerializer(data=bill, context={'request':request})
            if serializer.is_valid():
                try:
                    serializer.save()
                except IntegrityError:
                    return Response({'details': "Bill exists with provided details.Integrity Error"}, status=400)
            else:
                conflict_invoices.append(bill['invoice_number'])
                ConflictBillNumber.objects.create(invoice_number=bill['invoice_number'])
        if conflict_invoices:
            return Response({'details': conflict_invoices}, status=409)

        return Response({'details': 'Bills Created'}, status=201)

class BillCheckSumView(APIView):

    def post(self, request):
        fiscal_year = Organization.objects.last().current_fiscal_year

        bills = request.data.get('bills', [])
        if not bills:
            return Response({'details':"Bills is required"}, status=400)
        new_invoice_list:list = []
        for bill in bills:
            invoice_num = bill.get('invoice_number', None)
            fiscal_year = bill.get('fiscal_year', fiscal_year)

            if not Bill.objects.filter(invoice_number=invoice_num, fiscal_year=fiscal_year).exists():
                if bill.get('payment_mode').lower() == "complimentary":
                    if Bill.objects.filter(fiscal_year=fiscal_year, transaction_date_time=bill.get('transaction_date_time')).exists():
                        continue
                new_invoice_list.append(invoice_num)
                serializer = BillSerializer(data=bill, context={'request':request})
                serializer.is_valid(raise_exception=True)
                try:
                    serializer.save()
                except Exception as e:
                    pass
        return Response({'details': 'ok', 'created_invoices':new_invoice_list})
    
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, time
from accounting.models import TblJournalEntry, TblDrJournalEntry, TblCrJournalEntry
from bill.models import Bill  # Replace 'yourapp' with your actual app name
from django.db import transaction

class FixJournalEntryEntryDateForBills(APIView):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        bills = Bill.objects.all().order_by('id')
        updated = 0

        for bill in bills:
            bill_date = bill.created_at.date()
            bill_amount = bill.grand_total

            start_datetime = datetime.combine(bill_date, time.min)
            end_datetime = datetime.combine(bill_date, time.max)

            journal_entry = TblJournalEntry.objects.filter(
                created_at__range=(start_datetime, end_datetime),
                entry_date__isnull=True,
                journal_total=bill_amount,
                employee_name = "Created Automatically during Sale"
            ).order_by('id').first()

            if journal_entry:
                journal_entry.entry_date = bill.transaction_date
                journal_entry.save()
                updated += 1

        return Response({"status": "completed", "updated_entries": updated})
    
from purchase.models import Purchase
class Pur(APIView):
    @transaction.atomic()
    def get(self, request, *args, **kwargs):
        # Get all purchases without a linked journal
        purchases = Purchase.objects.all().order_by('id')
        updated_entries = 0

        for purchase in purchases:
            # Use created_at date instead of bill_date
            purchase_created_date = purchase.created_at.date()
            purchase_total = purchase.grand_total
            print(purchase_created_date)

            start_date = datetime.combine(purchase_created_date, datetime.min.time())
            end_date = datetime.combine(purchase_created_date, datetime.max.time())

            journal_entry = TblJournalEntry.objects.filter(
                created_at__range=(start_date, end_date),
                journal_total=purchase_total
            ).order_by('id').first()

            entry_date = purchase.bill_date
            if journal_entry:
                journal_entry.entry_date = entry_date
                journal_entry.save()

        return Response({"status": "completed", "updated_entries": updated_entries})

            