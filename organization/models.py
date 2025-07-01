from django.db import models
from root.utils import BaseModel, SingletonModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import environ
env = environ.Env(DEBUG=(bool, False))

class StaticPage(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    published_date = models.DateField(null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Organization(SingletonModel, BaseModel):
    # basic company details
    org_name = models.CharField(max_length=255)
    org_logo = models.ImageField(
        upload_to="organization/images/", null=True, blank=True
    )
    tax_number = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="PAN/VAT Number"
    )
    website = models.URLField(null=True, blank=True)
    current_fiscal_year = models.CharField(null=True, max_length=20)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    # contact details
    company_contact_number = models.CharField(max_length=255, null=True, blank=True)
    company_contact_email = models.EmailField(null=True, blank=True)
    contact_person_name = models.CharField(max_length=255, null=True, blank=True)
    contact_person_number = models.CharField(max_length=255, null=True, blank=True)
    company_address = models.CharField(max_length=255, null=True, blank=True)
    company_bank_qr = models.ImageField(
        upload_to="organization/images/", null=True, blank=True
    )
    loyalty_percentage =models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allow_negative_sales = models.BooleanField(default=False) 
    show_zero_ledgers = models.BooleanField(default=False)


    def __str__(self):
        return self.org_name
    
    def get_fiscal_year(self):
        return f'{self.start_year}-{self.end_year}'



from uuid import uuid4


def get_default_uuid():
    return uuid4().hex


class Branch(BaseModel):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=50, null=True, blank=True)
    branch_manager = models.CharField(max_length=255, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    branch_code = models.CharField(
        max_length=255, null=False, blank=False, unique=True, default=get_default_uuid
    )
    is_central_billing = models.BooleanField(default=False, verbose_name='For Central Billing (Web)')

    def __str__(self):
        return f"{self.organization.org_name} - {self.name} Branch"

    # def save(self, *args, **kwargs):
    #     unique_id = shortuuid.ShortUUID().random(length=3)
    #     branch_char_list = [b[0].upper() for b in self.name.split()]
    #     branch_code = "".join(branch_char_list)
    #     self.branch_code = f"{branch_code}-{str(unique_id).upper()}"
    #     super(Branch, self).save(*args, **kwargs)

    # return super().save(*args, **kwargs)


class EndDayRecord(BaseModel):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    terminal = models.CharField(max_length=10)
    date = models.DateField()

    def __str__(self):
        return self.branch.name



class MailRecipient(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MailSendRecord(models.Model):
    mail_recipient = models.ForeignKey(MailRecipient, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mail_recipient.name


class EndDayDailyReport(BaseModel):
    employee_name = models.CharField(max_length=50)
    net_sales = models.FloatField()
    vat = models.FloatField()
    total_discounts = models.FloatField()
    cash = models.FloatField()
    credit = models.FloatField()
    credit_card = models.FloatField()
    mobile_payment = models.FloatField()
    complimentary = models.FloatField()
    start_bill = models.CharField(max_length=20)
    end_bill = models.CharField(max_length=20)
    date_time = models.CharField(max_length=100, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    terminal = models.CharField(max_length=10, null=True)
    total_sale = models.FloatField(default=0)

    def __str__(self):
        return 'Report'
    
    def save(self, *args, **kwargs):
        self.total_sale = round(self.net_sales + self.vat, 2)
        return super().save()

from .utils import send_mail_to_receipients
from threading import Thread
from datetime import datetime
from organization.utils import get_mobilepayments, convert_to_dict
from itertools import groupby
from operator import itemgetter

@receiver(post_save, sender=EndDayDailyReport)
def create_profile(sender, instance, created, **kwargs):
    if created:
        sender = env('EMAIL_HOST_USER')
        mail_list = []
        recipients = MailRecipient.objects.filter(status=True)
        for r in recipients:
            mail_list.append(r.email)
            MailSendRecord.objects.create(mail_recipient=r)
        if mail_list:
            dt_now = datetime.now()
            date_now = dt_now.date()
            time_now = dt_now.time().strftime('%I:%M %p')
            org = Organization.objects.first().org_name
            mobilepaymenttype_queryset, total_per_type = get_mobilepayments(instance.branch, instance.terminal)
            mobilepaymenttype_dict = convert_to_dict(total_per_type) if mobilepaymenttype_queryset else None
            
            start_bill_number = int(instance.start_bill.split('-')[-1])
            end_bill_number = int(instance.end_bill.split('-')[-1])
            print(start_bill_number)
            print(end_bill_number)
            # bills = Bill.objects.filter(payment_mode="CREDIT")
            from bill.models import Bill
            # bills = Bill.objects.filter(payment_mode="CREDIT", invoice_number__gte=f'{instance.branch.branch_code}-{instance.terminal}-{start_bill_number}',
            #     invoice_number__lte=f'{instance.branch.branch_code}-{instance.terminal}-{end_bill_number}', branch=instance.branch).values('invoice_number', 'customer_name', 'grand_total')
            bills = Bill.objects.filter(
                payment_mode="CREDIT",
                invoice_number__range=[
                    f'{instance.branch.branch_code}-{instance.terminal}-{start_bill_number}',
                    f'{instance.branch.branch_code}-{instance.terminal}-{end_bill_number}'
                ],
                branch=instance.branch
            ).values('invoice_number', 'customer_name', 'grand_total')
            # print("Before looping", bills)
            # Group bills by customer_name
            # grouped_bills = {}
            # for key, group in groupby(bills, key=itemgetter('customer_name')):
            #     # Each group is a list of dictionaries
            #     bills_data = list(group)

            #     total_amount = sum(bill_data['grand_total'] for bill_data in bills_data)

            #     grouped_bills[key] = {
            #         'bills_data': bills_data,
            #         'total_amount': total_amount,
            #     }
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
            
            # Print or further process the grouped bills
            print(grouped_bills)
            
            report_data = {
                'org_name':org,
                'date_now': date_now,
                'time_now': time_now,
                'total_sale': instance.total_sale,
                'date_time':instance.date_time,
                'employee_name': instance.employee_name,
                'net_sales': instance.net_sales,
                'vat': instance.vat,  
                'total_discounts': instance.total_discounts,
                'cash': instance.cash,
                'credit': instance.credit,
                'credit_card': instance.credit_card,
                'mobile_payment': instance.mobile_payment,
                'complimentary': instance.complimentary,
                'start_bill': instance.start_bill,
                'end_bill': instance.end_bill,
                'branch': instance.branch.name,
                'terminal': instance.terminal,
                'mobilepaymenttype_dict': mobilepaymenttype_dict if mobilepaymenttype_dict else None,
                'grouped_bills': grouped_bills,


            }
            Thread(target=send_mail_to_receipients, args=(report_data, mail_list, sender)).start()
            
            if mobilepaymenttype_queryset is not None:
                for payment in mobilepaymenttype_queryset:
                    payment.sent_in_mail = True
                    payment.save()

            
class Terminal(BaseModel):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    terminal_no = models.PositiveIntegerField()
    # is_active = models.BooleanField(default=False)
    # active_count = models.IntegerField(default = 0)
    # dayclose = models.BooleanField(default=False)


    def __str__(self):
        return f'Terminal {self.terminal_no} of branch {self.branch.name}'


class PrinterSetting(BaseModel):

    PRINTER_LOCATION = (
        ('KITCHEN', "KITCHEN"),
        ("BAR", "BAR")
    )

    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    url = models.CharField(max_length=100, null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    printer_location = models.CharField(max_length=10, choices=PRINTER_LOCATION)
    print_status = models.BooleanField(default=False)

    def __str__(self):
        return f'Printer for terminal {self.terminal.terminal_no}'
    
    class Meta:
        unique_together = 'printer_location', 'terminal',