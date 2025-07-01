from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
from decimal import Decimal
from bill.models import Bill, BillItem


class TodaysTransactionAPIView(APIView):
    def get(self, request):
        today = date.today()
        bills = Bill.objects.filter(transaction_date=today, status=True)
        last_update = Bill.objects.order_by('-created_at').first().created_at if Bill.objects.exists() else None
        
        terminals = {}
        for bill in bills:
            if bill.invoice_number:
                bill_no_lst = bill.invoice_number.split('-')[:2]
                terminal_no = f"{bill_no_lst[0]}-{bill_no_lst[1]}"
                if terminal_no not in terminals:
                    last_updated = Bill.objects.filter(invoice_number__startswith=terminal_no).order_by('-created_at').first().created_at
                    terminals[terminal_no] = {"total_sale": Decimal(0), "vat": Decimal(0),
                                            "net_sale": Decimal(0), "discount": Decimal(0),
                                            "cash": Decimal(0), "food": Decimal(0), "beverage": Decimal(0), "others": Decimal(0),
                                            "credit_card": Decimal(0), "mobile_payment": Decimal(0), 'last_updated': last_updated }
                
                terminals[terminal_no]['total_sale'] += bill.grand_total
                terminals[terminal_no]['vat'] += bill.tax_amount
                terminals[terminal_no]['discount'] += bill.discount_amount
                terminals[terminal_no]['net_sale'] += (bill.grand_total - bill.tax_amount)

                if bill.payment_mode.lower().strip() == "cash":
                    terminals[terminal_no]['cash'] += bill.grand_total
                elif bill.payment_mode.lower().strip() == "credit card":
                    terminals[terminal_no]['credit_card'] += bill.grand_total
                elif bill.payment_mode.lower().strip() == "mobile payment":
                    terminals[terminal_no]['mobile_payment'] += bill.grand_total
                
                for item in bill.bill_items.all():
                    if item.product.category.title.lower().strip() == "food":
                        terminals[terminal_no]['food'] += item.amount
                    elif item.product.category.title.lower().strip() == "beverage":
                        terminals[terminal_no]['beverage'] += item.amount
                    elif item.product.category.title.lower().strip() == "others":
                        terminals[terminal_no]['others'] += item.amount
                

        terminals_to_response = []
        for terminal, data in terminals.items():
            data['terminal'] = terminal
            terminals_to_response.append(data)

        terminal_totals = {
            'total_sale': sum(terminals[terminal]['total_sale'] for terminal in terminals),
            'net_sale': sum(terminals[terminal]['net_sale'] for terminal in terminals),
            'vat': sum(terminals[terminal]['vat'] for terminal in terminals),
            'discount': sum(terminals[terminal]['discount'] for terminal in terminals),
            'credit_card': sum(terminals[terminal]['credit_card'] for terminal in terminals),
            'mobile_payment': sum(terminals[terminal]['mobile_payment'] for terminal in terminals),
            'cash': sum(terminals[terminal]['cash'] for terminal in terminals),
        }

        response_data = {
            'terminals': terminals_to_response,
            'last_update': last_update,
            'terminal_totals': terminal_totals
        }

        return Response(response_data, 200)
