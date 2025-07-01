from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from datetime import datetime
from organization.models import EndDayDailyReport
from api.serializers.report import EnddaySerializer, PaymentModeSerializer

class EndDayReportAPIView(APIView):
    def post(self, request):
        # Retrieve fromDate and toDate from query parameters
        data = request.data
        branch = data.get('branch', None)

        if branch:
            queryset = EndDayDailyReport.objects.filter(branch__id=int(branch))
        else:
            queryset = EndDayDailyReport.objects.all()
        from_date_str = request.GET.get('fromDate')
        to_date_str = request.GET.get('toDate')

        # Convert fromDate and toDate strings to datetime objects
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None

        # Retrieve end day reports based on date range
        if from_date and to_date:
            reports = []

            for report in queryset.order_by('created_at'):
                report_datetime = datetime.strptime(report.date_time, '%Y-%m-%dT%H:%M:%S.%f')
                # Check if the report_date falls within the specified range
                if from_date.date() <= report_datetime.date() <= to_date.date():
                    reports.append(report)
            
            # Serialize the reports data if needed

        else:
            # Retrieve all reports if no date range specified
            reports = queryset.order_by('-created_at')

        serializer = EnddaySerializer(reports, many=True)

        # Return the response
        return Response(serializer.data, 200)
    
class EndDayReportDayWiseAPIView(APIView):
    def get(self, request):
        # Retrieve fromDate and toDate from query parameters
        from_date_str = request.GET.get('fromDate')
        to_date_str = request.GET.get('toDate')

        # Convert fromDate and toDate strings to datetime objects
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None

        # Retrieve end day reports based on date range
        if from_date and to_date:
            reports = []

            daily_totals = {
                "Sun": 0.0,
                "Mon": 0.0,
                "Tue": 0.0,
                "Wed": 0.0,
                "Thu": 0.0,
                "Fri": 0.0,
                "Sat": 0.0,
            }

            for report in EndDayDailyReport.objects.all().order_by('created_at'):
                report_datetime = datetime.strptime(report.date_time, '%Y-%m-%dT%H:%M:%S.%f')
                # Check if the report_date falls within the specified range
                if from_date.date() <= report_datetime.date() <= to_date.date():
                    reports.append(report)

            
            print(reports)

            for daywise_report in reports:
                report_datetime = datetime.strptime(daywise_report.date_time, '%Y-%m-%dT%H:%M:%S.%f')
                day_of_week = report_datetime.weekday()
                
                # Convert day of the week index to day name
                day_name = report_datetime.strftime('%a')
                
                # Add total_sale to the corresponding day in daily_totals
                daily_totals[day_name] += daywise_report.total_sale
            
            # Serialize the reports data if needed

            # print(daily_totals)
            return Response(daily_totals, 200)
        else:
            # Retrieve all reports if no date range specified
            return Response("No date has been provided", 400)

        # serializer = EnddaySerializer(reports, many=True)

        # Return the response
from organization.models import Branch
from bill.models import Bill, BillPayment
from decimal import Decimal

class SummaryReport(APIView):
    def post(self, request, *args, **kwargs):

        data = request.data

        branch = data['branch']

        from_date_str = request.GET.get('fromDate')
        to_date_str = request.GET.get('toDate')

        branch = Branch.objects.get(pk=branch)
        # Convert fromDate and toDate strings to datetime objects
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None

        if from_date and to_date:
            reports = []

            daily_totals = {
                "Sun": 0.0,
                "Mon": 0.0,
                "Tue": 0.0,
                "Wed": 0.0,
                "Thu": 0.0,
                "Fri": 0.0,
                "Sat": 0.0,
            }

            for report in EndDayDailyReport.objects.filter(branch=branch).order_by('created_at'):
                # report_datetime = datetime.strptime(report.date_time, '%Y-%m-%dT%H:%M:%S.%f')
                # Check if the report_date falls within the specified range
                if from_date.date() <= report.created_at.date() <= to_date.date():
                    reports.append(report)

            
            print(reports)

            for daywise_report in reports:
                report_datetime = daywise_report.created_at
                day_of_week = report_datetime.weekday()
                
                # Convert day of the week index to day name
                day_name = report_datetime.strftime('%a')
                
                # Add total_sale to the corresponding day in daily_totals
                daily_totals[day_name] += daywise_report.total_sale


            new_daily_totals = {
                "Sun": Decimal(0.0),
                "Mon": Decimal(0.0),
                "Tue": Decimal(0.0),
                "Wed": Decimal(0.0),
                "Thu": Decimal(0.0),
                "Fri": Decimal(0.0),
                "Sat": Decimal(0.0),
            }

            queryset1 = Bill.objects.filter(status=True, branch=branch, 
                                            transaction_date__gte=from_date,
                                            transaction_date__lte=to_date)
            
            # Iterate through the queryset and aggregate totals
            for bill in queryset1:
                day_of_week = bill.transaction_date.strftime('%a')  # 'Sun', 'Mon', etc.
                new_daily_totals[day_of_week] += bill.grand_total

            bill_ids = queryset1.values_list('id', flat=True)

            possible_payment_modes = ["CASH", "CREDIT", "COMPLIMENTARY", "CREDIT CARD", "MOBILE PAYMENT"]

            possible_payment_modes = ["CASH", "CREDIT", "COMPLIMENTARY", "CREDIT CARD", "MOBILE PAYMENT"]

            # Initialize a dictionary to store the payment mode totals
            payment_mode_totals = {mode: Decimal(0.0) for mode in possible_payment_modes}

            # Get the total amount for each payment mode
            bill_payments = BillPayment.objects.filter(bill_id__in=bill_ids)

            for payment in bill_payments:
                # Update the total for each payment mode
                payment_mode_totals[payment.payment_mode] += payment.amount

            # Create a list of payment mode data
            payment_mode_data = [
                {"payment_mode": mode, "total_amount": payment_mode_totals[mode]}
                for mode in possible_payment_modes
            ]

            payment_mode_serializer = PaymentModeSerializer(payment_mode_data, many=True)
            bill_items_total = self.calculate_bill_items_total(queryset1)

            response_data = {
                "fromDate":from_date_str, 
                "toDate":to_date_str,
                "days": daily_totals, 
                "new_days": new_daily_totals,
                "payment": payment_mode_serializer.data,
                "bill_items_total": bill_items_total,

            }

            return Response(response_data, 200)

        else:
            # Retrieve all reports if no date range specified
            return Response("No date has been provided", 400)
        
    def calculate_bill_items_total(self, queryset):
            bill_items_total = []

            # Create a dictionary to store product quantities
            product_quantities = {}

            for bill in queryset:
                for bill_item in bill.bill_items.all():
                    product_id = bill_item.product.id
                    quantity = bill_item.product_quantity
                    rate = bill_item.rate
                    product_category = bill_item.product.category.title 
                    # product_group = bill_item.product.group
                  
                    product_title = bill_item.product_title

                    key = (product_id, rate)
                    if key in product_quantities:
                        product_quantities[key]['quantity'] += quantity
                    else:
                        product_quantities[key] = {
                        'quantity': quantity,
                        'rate': rate,
                        'product_title': product_title,
                        'category': product_category 
                        # 'group': product_group
                    }

            for product_id, item_data in product_quantities.items():
                bill_items_total.append({
                    'product_title': item_data['product_title'],
                    'product_quantity': item_data['quantity'],
                    'rate': item_data['rate'],
                    'amount': item_data['quantity'] * item_data['rate'],
                    'category': item_data['category'] ,
                    # 'group': item_data['group']
                })

            bill_items_total = sorted(bill_items_total, key=lambda x: x['product_quantity'], reverse=True)

            return bill_items_total
    

from rest_framework import generics
from bill.models import Bill, BillPayment
from api.serializers.report import BillSerializer,PaymentModeSerializer
from rest_framework import status
from decimal import Decimal
import jwt
from organization.models import Branch, Terminal
from django.db.models import Sum
from product.models import Product
from collections import defaultdict
from django.utils import timezone

class MasterBillDetailView(generics.ListAPIView):
    serializer_class = BillSerializer  # Assuming the URL parameter is 'id'

    def get_queryset(self):


        pass

    def list(self, request, *args, **kwargs):
        from_date_str = request.GET.get('fromDate')

        to_date_str = request.GET.get('toDate')

        branches = Branch.objects.filter(is_deleted=False, status=True)
        response_list = []
        total_bills = 0
        total_bill_items = 0
        total_beverage_items = 0
        total_food_items = 0
        total_others_items = 0
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None
        
        total = {
                'discount_amount': Decimal(0.0),
                'taxable_amount': Decimal(0.0),
                'tax_amount': Decimal(0.0),
                'grand_total': Decimal(0.0),
                'service_charge': Decimal(0.0),
                'CASH': Decimal(0.0),
                'CREDIT': Decimal(0.0),
                'COMPLIMENTARY': Decimal(0.0),
                'CREDIT CARD': Decimal(0.0),
                'MOBILE PAYMENT': Decimal(0.0),
            }
            
        total_queryset = Bill.objects.filter(transaction_date__gte=from_date,
                                            transaction_date__lte=to_date)

        bill_items_total = self.calculate_bill_items_total(total_queryset)

        for branch in branches:
        # queryset, queryset1 = self.get_queryset()


            queryset = Bill.objects.filter( branch=branch,transaction_date__gte=from_date,
                                            transaction_date__lte=to_date)
            queryset1 = Bill.objects.filter( status=True, branch=branch,transaction_date__gte=from_date,
                                            transaction_date__lte=to_date)

            no_of_bills = queryset1.count()

            total_bills += no_of_bills
            # Get the IDs of bills with is_end_day=False
            bill_ids = queryset1.values_list('id', flat=True)

            possible_payment_modes = ["CASH", "CREDIT", "COMPLIMENTARY", "CREDIT CARD", "MOBILE PAYMENT"]

            # Initialize a dictionary to store the payment mode totals
            payment_mode_totals = {mode: Decimal(0.0) for mode in possible_payment_modes}

            # Get the total amount for each payment mode
            bill_payments = BillPayment.objects.filter(bill_id__in=bill_ids)

            for payment in bill_payments:
                # Update the total for each payment mode
                payment_mode_totals[payment.payment_mode] += payment.amount

            # Create a list of payment mode data
            payment_mode_data = [
                {"payment_mode": mode, "total_amount": payment_mode_totals[mode]}
                for mode in possible_payment_modes
            ]


            # Calculate the invoice_number and grand_total for void bills
            # void_bills_data = queryset.filter(status=False).values('invoice_number', 'grand_total')

            # Serialize the payment_mode_data
            payment_mode_serializer = PaymentModeSerializer(payment_mode_data, many=True)

            terminals = Terminal.objects.filter(status=True, is_deleted=False)

            terminalwisestartend_list = []

            for terminal in terminals:

                startend_queryset = Bill.objects.filter( status=True, branch=branch,transaction_date__gte=from_date,
                                            transaction_date__lte=to_date, terminal=terminal.terminal_no)
                first_bill = None
                last_bill = None

                for bill in startend_queryset:
                    if not first_bill and bill.invoice_number:
                        first_bill = bill
                    if bill.invoice_number:
                        last_bill = bill

                # If no bill with a non-null invoice number is found for the last bill, use the last bill
                if last_bill is None:
                    last_bill = startend_queryset.last()

                starting_from_invoice = first_bill.invoice_number if first_bill else None
                ending_from_invoice = last_bill.invoice_number if last_bill else None
                if startend_queryset:
                    terminalwise_startend_dict = {
                        "terminal": terminal.terminal_no,
                        "Starting_from":starting_from_invoice,
                        "Ending_from": ending_from_invoice
                    }

                    terminalwisestartend_list.append(terminalwise_startend_dict)
            
            sub_total_sum = Decimal(0)
            discount_amount_sum = Decimal(0)
            taxable_amount_sum = Decimal(0)
            tax_amount_sum = Decimal(0)
            grand_total_sum = Decimal(0)
            service_charge_sum = Decimal(0)

            for bill in queryset1:
                if bill.payment_mode != 'COMPLIMENTARY':
                    sub_total_sum += bill.sub_total
                    discount_amount_sum += bill.discount_amount
                    taxable_amount_sum += bill.taxable_amount
                    tax_amount_sum += bill.tax_amount
                    grand_total_sum += bill.grand_total
                    service_charge_sum += bill.service_charge
            # bill_items_total = self.calculate_bill_items_total(queryset)

            serializer = self.get_serializer(queryset, many=True)

            # Create a response dictionary with "bill_data" key
            response_data = {
                # "bill_data": serializer.data,
                'branch': branch.name,
                'branch_id':branch.id,
                "payment_modes": payment_mode_serializer.data,
                # "Starting_from":starting_from_invoice,
                # "Ending_from":ending_from_invoice,
                "startend": terminalwisestartend_list
                # "bill_items_total": bill_items_total,
            }


            # Calculate and add the sales data to the response
            sales_data = {
                'discount_amount': discount_amount_sum,
                'taxable_amount': taxable_amount_sum,
                'tax_amount': tax_amount_sum,
                'grand_total': grand_total_sum,
                'service_charge': service_charge_sum,
            }
            response_data['Sales'] = sales_data
            total_items = queryset.filter(
                is_end_day=False
            ).aggregate(items_total=Sum('bill_items__product_quantity'))['items_total'] or 0

            total_bill_items += total_items

            # response_data['food_total'] = food_total
            # response_data['beverage_total'] = beverage_total
            # response_data['others_total'] = others_total
            response_data['no_of_bills'] = no_of_bills


            # total['food_total'] += food_total
            # total['beverage_total'] += beverage_total
            # total['others_total'] += others_total
            total['discount_amount'] += discount_amount_sum
            total['taxable_amount'] += taxable_amount_sum
            total['tax_amount'] += tax_amount_sum
            total['grand_total'] += grand_total_sum
            total['service_charge'] += service_charge_sum
            total['no_of_bills'] = total_bills

            for payment_data in payment_mode_data:
                total['CASH'] += payment_data['total_amount'] if payment_data['payment_mode'] == 'CASH' else Decimal(0.0)
                total['CREDIT'] += payment_data['total_amount'] if payment_data['payment_mode'] == 'CREDIT' else Decimal(0.0)
                total['COMPLIMENTARY'] += payment_data['total_amount'] if payment_data['payment_mode'] == 'COMPLIMENTARY' else Decimal(0.0)
                total['CREDIT CARD'] += payment_data['total_amount'] if payment_data['payment_mode'] == 'CREDIT CARD' else Decimal(0.0)
                total['MOBILE PAYMENT'] += payment_data['total_amount'] if payment_data['payment_mode'] == 'MOBILE PAYMENT' else Decimal(0.0)


            response_list.append(response_data)

        actual_response = {
            "data": response_list, 
            "totals": total,
            "total_items": int(total_bill_items),
            "fromDate": from_date_str,
            "toDate": to_date_str
            # "total_food_items": int(total_food_items),
            # "total_beverage_items": int(total_beverage_items),
            # "total_others_items": int(total_others_items),
            # "foods": bill_items_total.get('FOOD', []),
            # "beverages": bill_items_total.get('BEVERAGE', []),
            # "others": bill_items_total.get('OTHERS', []) ,

        }

        return Response(actual_response, status=status.HTTP_200_OK)
    
    def calculate_bill_items_total(self, queryset):
        bill_items_total = defaultdict(list)

        # Create a dictionary to store product quantities
        product_quantities = defaultdict(lambda: {'quantity': 0, 'rate': 0, 'product_title': ''})

        for bill in queryset:
            for bill_item in bill.bill_items.all():
                product_id = bill_item.product.id
                quantity = bill_item.product_quantity
                rate = bill_item.rate
                product_title = bill_item.product_title
                product_category = bill_item.product.category.title  # Assuming 'type' is the related field to ProductCategory

                key = (product_id, rate)
                if key in product_quantities:
                    product_quantities[key]['quantity'] += quantity
                else:
                    product_quantities[key] = {
                        'quantity': quantity,
                        'rate': rate,
                        'product_title': product_title,
                        'type': product_category
                    }

                # Append the bill item to the corresponding category list
        # current_date = timezone.date
        for product_id, item_data in product_quantities.items():
                bill_items_total[item_data['type']].append({
                    'product_title': item_data['product_title'],
                    'product_quantity': item_data['quantity'],
                    'rate': item_data['rate'],
                    'amount': item_data['quantity'] * item_data['rate'],
                })

        # Convert defaultdict to regular dict for JSON serialization
        bill_items_total = dict(bill_items_total)

        return bill_items_total


from rest_framework import generics
from rest_framework import status
from django.db.models import Sum
from product.models import Product
from api.serializers.report import BillSerializer
from django.utils import timezone

class BillDetailView(generics.ListAPIView):
    serializer_class = BillSerializer  # Assuming the URL parameter is 'id'

    def get_queryset(self):


        pass

    def post(self, request, *args, **kwargs):
        current_date = timezone.now().date()  
        from_date_str = request.GET.get('fromDate')

        to_date_str = request.GET.get('toDate')

        branch = request.data['branch']
        
        # Convert fromDate and toDate strings to datetime objects
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None

        branch = Branch.objects.get(pk=branch)
        queryset = Bill.objects.filter(branch=branch,transaction_date__gte=from_date,
                                            transaction_date__lte=to_date)
        queryset1 = Bill.objects.filter(status=True, branch=branch,transaction_date__gte=from_date,
                                            transaction_date__lte=to_date)
        # queryset, queryset1 = self.get_queryset()

        # Get the IDs of bills with is_end_day=False
        bill_ids = queryset1.values_list('id', flat=True)

        possible_payment_modes = ["CASH", "CREDIT", "COMPLIMENTARY", "CREDIT CARD", "MOBILE PAYMENT"]

        # Initialize a dictionary to store the payment mode totals
        payment_mode_totals = {mode: Decimal(0.0) for mode in possible_payment_modes}

        # Get the total amount for each payment mode
        bill_payments = BillPayment.objects.filter(bill_id__in=bill_ids)

        for payment in bill_payments:
            # Update the total for each payment mode
            payment_mode_totals[payment.payment_mode] += payment.amount

        # Create a list of payment mode data
        payment_mode_data = [
            {"payment_mode": mode, "total_amount": payment_mode_totals[mode]}
            for mode in possible_payment_modes
        ]


        # Calculate the invoice_number and grand_total for void bills
        void_bills_data = queryset.filter(status=False).values('invoice_number', 'grand_total')

        # Serialize the payment_mode_data
        # payment_mode_serializer = PaymentModeSerializer(payment_mode_data, many=True)
        # first_bill = None
        # last_bill = None

        # for bill in queryset:
        #     if not first_bill and bill.invoice_number:
        #         first_bill = bill
        #     if bill.invoice_number:
        #         last_bill = bill

        # # If no bill with a non-null invoice number is found for the last bill, use the last bill
        # if last_bill is None:
        #     last_bill = queryset.last()

        # starting_from_invoice = first_bill.invoice_number if first_bill else None
        # ending_from_invoice = last_bill.invoice_number if last_bill else None

        
        # sub_total_sum = Decimal(0)
        # discount_amount_sum = Decimal(0)
        # taxable_amount_sum = Decimal(0)
        # tax_amount_sum = Decimal(0)
        # grand_total_sum = Decimal(0)
        # service_charge_sum = Decimal(0)

        # for bill in queryset1:
        #     if bill.payment_mode != 'COMPLIMENTARY':
        #         sub_total_sum += bill.sub_total
        #         discount_amount_sum += bill.discount_amount
        #         taxable_amount_sum += bill.taxable_amount
        #         tax_amount_sum += bill.tax_amount
        #         grand_total_sum += bill.grand_total
        #         service_charge_sum += bill.service_charge
        bill_items_total = self.calculate_bill_items_total(queryset1)

        # serializer = self.get_serializer(queryset, many=True)

        # # Create a response dictionary with "bill_data" key
        # response_data = {
        #     "fromDate": from_date_str,
        #     "toDate": to_date_str,
        #     "bill_data": serializer.data,
        #     "payment_modes": payment_mode_serializer.data,
        #     "Starting_from":starting_from_invoice,
        #     "Ending_from":ending_from_invoice,
        #     "bill_items_total": bill_items_total,

        # }
        payment_mode_serializer = PaymentModeSerializer(payment_mode_data, many=True)

        terminals = Terminal.objects.filter(status=True, is_deleted=False)

        terminalwisestartend_list = []

        for terminal in terminals:

            startend_queryset = Bill.objects.filter( status=True, branch=branch,transaction_date__gte=from_date,
                                            transaction_date__lte=to_date, terminal=terminal.terminal_no)
            first_bill = None
            last_bill = None

            for bill in startend_queryset:
                if not first_bill and bill.invoice_number:
                    first_bill = bill
                if bill.invoice_number:
                    last_bill = bill

                # If no bill with a non-null invoice number is found for the last bill, use the last bill
            if last_bill is None:
                last_bill = startend_queryset.last()

            starting_from_invoice = first_bill.invoice_number if first_bill else None
            ending_from_invoice = last_bill.invoice_number if last_bill else None
            if startend_queryset:
                terminalwise_startend_dict = {
                    "terminal": terminal.terminal_no,
                    "Starting_from":starting_from_invoice,
                    "Ending_from": ending_from_invoice
                }

                terminalwisestartend_list.append(terminalwise_startend_dict)
            
            sub_total_sum = Decimal(0)
            discount_amount_sum = Decimal(0)
            taxable_amount_sum = Decimal(0)
            tax_amount_sum = Decimal(0)
            grand_total_sum = Decimal(0)
            service_charge_sum = Decimal(0)

            for bill in queryset1:
                if bill.payment_mode != 'COMPLIMENTARY':
                    sub_total_sum += bill.sub_total
                    discount_amount_sum += bill.discount_amount
                    taxable_amount_sum += bill.taxable_amount
                    tax_amount_sum += bill.tax_amount
                    grand_total_sum += bill.grand_total
                    service_charge_sum += bill.service_charge
            # bill_items_total = self.calculate_bill_items_total(queryset)

            serializer = self.get_serializer(queryset, many=True)

            # Create a response dictionary with "bill_data" key
            response_data = {
                "bill_data": serializer.data,
                'branch': branch.name,
                'branch_id':branch.id,
                "payment_modes": payment_mode_serializer.data,
                # "Starting_from":starting_from_invoice,
                # "Ending_from":ending_from_invoice,
                "startend": terminalwisestartend_list,
                "bill_items_total": bill_items_total,
            }

        # Calculate and add the sales data to the response
        sales_data = {
            'discount_amount': discount_amount_sum,
            'taxable_amount': taxable_amount_sum,
            'tax_amount': tax_amount_sum,
            'grand_total': grand_total_sum,
            'service_charge': service_charge_sum,
        }
        response_data['Sales'] = sales_data

        # Add void bills data to the response
        response_data['void_bills'] = void_bills_data

        return Response(response_data, status=status.HTTP_200_OK)
    
    def calculate_bill_items_total(self, queryset):
            bill_items_total = []

            # Create a dictionary to store product quantities
            product_quantities = {}

            for bill in queryset:
                for bill_item in bill.bill_items.all():
                    product_id = bill_item.product.id
                    quantity = bill_item.product_quantity
                    rate = bill_item.rate
                    product_category = bill_item.product.category.title 
                    # product_group = bill_item.product.group
                  
                    product_title = bill_item.product_title

                    key = (product_id, rate)
                    if key in product_quantities:
                        product_quantities[key]['quantity'] += quantity
                    else:
                        product_quantities[key] = {
                        'quantity': quantity,
                        'rate': rate,
                        'product_title': product_title,
                        'category': product_category ,
                        # 'group': product_group
                    }

            for product_id, item_data in product_quantities.items():
                bill_items_total.append({
                    'product_title': item_data['product_title'],
                    'product_quantity': item_data['quantity'],
                    'rate': item_data['rate'],
                    'amount': item_data['quantity'] * item_data['rate'],
                    'category': item_data['category'] ,
                    # 'group': item_data['group']
                })

            return bill_items_total
            
from user.models import Customer
class CustomerBills(APIView):
    def post(self, request, *args, **kwargs):
        customer_name = request.data.get('customer_name')
        customer_bills = Bill.objects.filter(customer_name__icontains=customer_name)

        bills = BillSerializer(customer_bills, many=True)

        return Response(bills.data, 200)