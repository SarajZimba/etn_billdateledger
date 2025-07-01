from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_mail_to_receipients(data, mail_list, sender):
    email_body = render_to_string('organization/mail_template.html', data)
    try:
        send_mail(
            'End Day Report',
            '',
            sender,
            mail_list,
            fail_silently=False,
            html_message=email_body
        )
    except Exception:
        pass
    

def send_combined_mail_to_receipients(combine_data, terminals_data,mail_list, sender):
    email_body = render_to_string('organization/combined_end_day_report_list.html', {'combine_data':combine_data, 'terminals_data':terminals_data})
    try:
        send_mail(
            'End Day Report',
            '',
            sender,
            mail_list,
            fail_silently=False,
            html_message=email_body
        )
    except Exception as e:
        print("Exception Occured", e)

from django.db.models import Sum
def get_mobilepayments(branch, terminal):
    from bill.models import MobilePaymentSummary
    mobilepayment_summary = MobilePaymentSummary.objects.filter(branch=branch, terminal=terminal, sent_in_mail=False) 

    if mobilepayment_summary:
        total_per_type = mobilepayment_summary.values('type__name').annotate(total_value=Sum('value'))

        # # Convert the queryset to a dictionary
        # total_per_type_dict = {item['type__name']: item['total_value'] for item in total_per_type}


        # print(total_per_type)
        return mobilepayment_summary,total_per_type
    else:
        return None, None

# convert_to_dict = get_mobilepayments(3, 2)

def convert_to_dict(value):
    # Convert the queryset to a dictionary
    if value:
        total_per_type_dict = {item['type__name']: item['total_value'] for item in value}   

        return total_per_type_dict
    else:
        return None
        
    
from django.db.models import Q
from organization.models import Organization
import environ
env = environ.Env(DEBUG=(bool, False))
from django.db.models import Sum
from itertools import groupby
from operator import itemgetter
def mobile_payment_func(endday):

        # org = Organization.objects.first().org_name
        from bill.models import Bill

        start_bill_number = int(endday.start_bill.split('-')[-1])
        end_bill_number = int(endday.end_bill.split('-')[-1])
        # bills = Bill.objects.filter(payment_mode="CREDIT", invoice_number__gte=f'{instance.branch.branch_code}-{instance.terminal}-{start_bill_number}',
        #     invoice_number__lte=f'{instance.branch.branch_code}-{instance.terminal}-{end_bill_number}', branch=instance.branch).values('invoice_number', 'customer_name', 'grand_total')
        bill_ids = Bill.objects.filter(
            Q(payment_mode="MOBILE PAYMENT") | Q(payment_mode="SPLIT"),
            invoice_number__range=[
            f'{endday.branch.branch_code}-{endday.terminal}-{start_bill_number}',
            f'{endday.branch.branch_code}-{endday.terminal}-{end_bill_number}'
            ],
            branch=endday.branch,
            terminal = endday.terminal
        ).values_list('id', flat=True)
        # print(bill_ids)
        from bill.models import MobilePaymentSummary

        summary_data = MobilePaymentSummary.objects.filter(
            bill__id__in=bill_ids
        ).values('type__name').annotate(total_value=Sum('value'))

        formatted_summary = [
            {'type': item['type__name'], 'total': item['total_value']}
            for item in summary_data
        ]

        return formatted_summary


def check_end_day_terminal():
    from bill.models import Bill
    from organization.models import Terminal, Branch, EndDayDailyReport
    branches = Branch.objects.filter(is_deleted=False, status=True)
    print(branches)
    end_day=False
    for branch in branches:
        terminals = branch.terminal_set.filter(is_deleted=False, status=True)
        print(terminals)
        for terminal in terminals:
            if EndDayDailyReport.objects.filter(status=True, terminal=terminal.terminal_no, branch=branch).exists():
                end_day=True
            else:
                if Bill.objects.filter(is_end_day=False, status=True, terminal=terminal.terminal_no, branch=branch).exists():
                    end_day=False
                    break
                else:
                    end_day=True
    return end_day
    # print(f"from end_day check {end_day}")


def get_credit(endday):
    start_bill_number = int(endday.start_bill.split('-')[-1])
    end_bill_number = int(endday.end_bill.split('-')[-1])
    print(start_bill_number)
    print(end_bill_number)
    # bills = Bill.objects.filter(payment_mode="CREDIT")
    from bill.models import Bill
    # bills = Bill.objects.filter(payment_mode="CREDIT", invoice_number__gte=f'{endday.branch.branch_code}-{endday.terminal}-{start_bill_number}',
    #     invoice_number__lte=f'{endday.branch.branch_code}-{endday.terminal}-{end_bill_number}', branch=endday.branch).values('invoice_number', 'customer_name', 'grand_total')
    bills = Bill.objects.filter(
                payment_mode="CREDIT",
                invoice_number__range=[
                    f'{endday.branch.branch_code}-{endday.terminal}-{start_bill_number}',
                    f'{endday.branch.branch_code}-{endday.terminal}-{end_bill_number}'
                ],
                branch=endday.branch
            ).values('invoice_number', 'customer_name', 'grand_total')
    print("before sorting", bills)
    sorted_bills = sorted(bills, key=itemgetter('customer_name'))
            
    print("after sorting", sorted_bills)
            # Group bills by customer_name
    grouped_bills = {}
    for key, group in groupby(sorted_bills, key=itemgetter('customer_name')):
                # Convert the group iterator to a list of dictionaries
        bills_data = list(group)
            
                # Calculate the total amount for each customer's bills
        total_amount = sum(bill_data['grand_total'] for bill_data in bills_data)
            
                # Store the grouped data in a dictionary
        grouped_bills[key] = {
                    'bills_data': bills_data,
                    'total_amount': total_amount
                }
        
    return grouped_bills
        
