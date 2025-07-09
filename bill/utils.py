from accounting.models import AccountChart, AccountLedger, TblCrJournalEntry, TblJournalEntry, TblDrJournalEntry, CumulativeLedger
from accounting.models import AccountSubLedger, AccountLedger, AccountChart
from purchase.models import AccountProductTracking
from decimal import Decimal
from product.models import Product

"""
Signal to update Cumulative Ledger
"""
from datetime import date
def update_cumulative_ledger_bill(instance, entry_date):
    ledger = CumulativeLedger.objects.filter(ledger=instance).last()
    if ledger :
        total_value = ledger.total_value
    else:
        total_value = Decimal(0.0)
    value_changed = instance.total_value - total_value
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        if value_changed > 0:
                CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date)
    else:
        if value_changed > 0:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date)

def update_cumulative_ledger_expense(instance, journal, entry_datetime):
    ledger = CumulativeLedger.objects.filter(ledger=instance).last()
    if ledger :
        total_value = ledger.total_value
    else:
        total_value = Decimal(0.0)
    value_changed = instance.total_value - total_value
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        if value_changed > 0:
                CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, journal=journal, entry_date=entry_datetime)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, journal=journal, entry_date=entry_datetime)
    else:
        if value_changed > 0:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, journal=journal, entry_date=entry_datetime)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, journal=journal, entry_date=entry_datetime)

def create_cumulative_ledger_bill(instance, entry_date):
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=instance.total_value, ledger=instance, debit_amount=instance.total_value, entry_date=entry_date)
    else:
        CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=instance.total_value, ledger=instance, credit_amount=instance.total_value, entry_date=entry_date)
    # if instance.account_chart.group == "Sundry Debtors":
    #     journal = TblJournalEntry.objects.create(employee_name=f"From Debtors form {instance.ledger_name}", journal_total=instance.total_value)
    #     TblDrJournalEntry.objects.create(ledger=instance, debit_amount=instance.total_value, particulars=f"Automatic: {instance.ledger_name} a/c Dr", journal_entry=journal)


    # if instance.account_chart.group == "Sundry Creditors":
    #     journal = TblJournalEntry.objects.create(employee_name=f"From Creditors form {instance.ledger_name}", journal_total=instance.total_value)
    #     TblCrJournalEntry.objects.create(ledger=instance, credit_amount=instance.total_value, particulars=f"Automatic: To {instance.ledger_name}", journal_entry=journal)



def create_journal_for_complimentary(instance):
    grand_total = Decimal(instance.sub_total)
    complimentary_sales = AccountLedger.objects.get(ledger_name__iexact='complimentary sales')
    complimentary_expenses = AccountLedger.objects.get(ledger_name__iexact='complimentary expenses')

    journal_entry = TblJournalEntry.objects.create(employee_name='Created automatically during sale', journal_total=grand_total)
    TblDrJournalEntry.objects.create(particulars="Complimentary Expenses A/C Dr.", debit_amount = grand_total, journal_entry=journal_entry, ledger=complimentary_expenses)
    TblCrJournalEntry.objects.create(particulars="To Complimentary Sales", credit_amount = grand_total, journal_entry=journal_entry, ledger=complimentary_sales)
    
    complimentary_expenses.total_value += grand_total
    complimentary_expenses.save()

    complimentary_sales.total_value += grand_total
    complimentary_sales.save()


def create_journal_for_bill(instance):
    print(instance.amount_in_words)
    payment_mode = instance.payment_mode.lower().strip()
    print(payment_mode)
    
    grand_total = Decimal(instance.grand_total)
    tax_amount = Decimal(instance.tax_amount)
    discount_amount = Decimal(instance.discount_amount)
    invoice_number = instance.invoice_number
    excise_duty_amount = Decimal(instance.excise_duty_amount)
    entry_date = instance.transaction_date_time
    narration = instance.narration

    if narration and narration != '':
        employee_name = narration + " from bill " + str(instance.invoice_number)
    else:
        employee_name = 'Created Automatically during Sale' + " from bill " + str(instance.invoice_number)
    sale_ledger = AccountLedger.objects.get(ledger_name='Sales')
    journal_entry = TblJournalEntry.objects.create(employee_name=employee_name, journal_total=(grand_total-discount_amount), entry_date=entry_date)


    if discount_amount > 0:
        discount_expenses = AccountLedger.objects.get(ledger_name__iexact='Discount Expenses')
        discount_sales = AccountLedger.objects.get(ledger_name__iexact='Discount Sales')

        TblDrJournalEntry.objects.create(particulars="Discount Expenses A/C Dr.", debit_amount = discount_amount, journal_entry=journal_entry, ledger=discount_expenses)
        TblCrJournalEntry.objects.create(particulars="To Discount Sales", credit_amount = discount_amount, journal_entry=journal_entry, ledger=discount_sales)
        
        discount_expenses.total_value += discount_amount
        discount_expenses.save()
        update_cumulative_ledger_bill(discount_expenses, entry_date)
        discount_sales.total_value += discount_amount
        discount_sales.save()
        update_cumulative_ledger_bill(discount_sales, entry_date)


    if tax_amount > 0:
        vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
        vat_payable.total_value = vat_payable.total_value + tax_amount
        vat_payable.save()
        update_cumulative_ledger_bill(vat_payable, entry_date)

        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To VAT Payable", ledger=vat_payable, credit_amount=tax_amount)
    
    if excise_duty_amount > 0:
        excise_duty_payable = AccountLedger.objects.get(ledger_name='Excise Duty Payable')
        excise_duty_payable.total_value = excise_duty_payable.total_value + excise_duty_amount
        excise_duty_payable.save()
        update_cumulative_ledger_bill(excise_duty_payable, entry_date)
        # update_cumulative_ledger_bill(excise_duty_payable)

        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Excise Duty Payable", ledger=excise_duty_payable, credit_amount=excise_duty_amount)

    if payment_mode == 'credit':
        account_chart = AccountChart.objects.get(group='Sundry Debtors')
        try:
            dr_ledger = AccountLedger.objects.get(ledger_name=f'{instance.customer.pk} - {instance.customer.name}')
            dr_ledger.total_value += grand_total
            dr_ledger.save()
            update_cumulative_ledger_bill(dr_ledger, entry_date)

        except AccountLedger.DoesNotExist:
            dr_ledger = AccountLedger.objects.create(ledger_name=f'{instance.customer.pk} - {instance.customer.name}', account_chart=account_chart, total_value=grand_total)
            create_cumulative_ledger_bill(dr_ledger, entry_date)

        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"{instance.customer.name} A/C Dr", ledger=dr_ledger, debit_amount=grand_total)
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount-excise_duty_amount))
        
        
    elif payment_mode == "credit card":
        card_transaction_ledger = AccountLedger.objects.get(ledger_name='Card Transactions')
        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Card Transaction A/C Dr", ledger=card_transaction_ledger, debit_amount=grand_total)
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount-excise_duty_amount))
        card_transaction_ledger.total_value += grand_total
        card_transaction_ledger.save()
        update_cumulative_ledger_bill(card_transaction_ledger, entry_date)

    elif payment_mode == "mobile payment":
        mobile_payment = AccountLedger.objects.get(ledger_name='Mobile Payments')

        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Mobile Payment A/C Dr", ledger=mobile_payment, debit_amount=grand_total)
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount-excise_duty_amount))
        mobile_payment.total_value += grand_total
        mobile_payment.save()
        update_cumulative_ledger_bill(mobile_payment, entry_date)

    elif payment_mode == "cash":
        cash_ledger = AccountLedger.objects.get(ledger_name='Cash-In-Hand')
        cash_ledger.total_value = cash_ledger.total_value + grand_total
        cash_ledger.save()
        update_cumulative_ledger_bill(cash_ledger, entry_date)

        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Sales from invoice number {invoice_number} Cash A/C Dr", ledger=cash_ledger, debit_amount=grand_total)
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount-excise_duty_amount))

    sale_ledger.total_value += (grand_total-tax_amount-excise_duty_amount)
    sale_ledger.save()
    update_cumulative_ledger_bill(sale_ledger, entry_date)
    # update_cumulative_ledger_bill(sale_ledger)


def update_subledger_after_updating_product(product_id, initial_name, updated_name):
    product = Product.objects.get(pk=product_id)
    subledgername = f'{initial_name} ({product.category.title})'
    AccountSubLedger.objects.filter(sub_ledger_name=subledgername).update(sub_ledger_name=f"{updated_name} ({product.category.title})")
    
from accounting.models import AccountSubLedgerTracking
def product_sold(instance):
    product = instance.product
    subledgername = f'{product.title} ({product.category.title}) - Sale'
    
    sale_ledger = AccountLedger.objects.get(ledger_name='Sales')
    try:
        print("I was in try")        
        sale_subledger = AccountSubLedger.objects.get(sub_ledger_name=subledgername, ledger=sale_ledger)
        prev_value = sale_subledger.total_value
        subledgertracking = AccountSubLedgerTracking.objects.create(subledger = sale_subledger, prev_amount= sale_subledger.total_value)
        sale_subledger.total_value += Decimal(instance.amount)
        sale_subledger.save()
        subledgertracking.new_amount=sale_subledger.total_value
        subledgertracking.value_changed = sale_subledger.total_value - prev_value
        subledgertracking.save()


    except AccountSubLedger.DoesNotExist:
        print("I was in the exception")
        subledger = AccountSubLedger.objects.create(sub_ledger_name=subledgername, ledger=sale_ledger, total_value=Decimal(instance.amount))
        subledgertracking = AccountSubLedgerTracking.objects.create(subledger=subledger, new_amount=Decimal(instance.amount), value_changed=Decimal(instance.amount))

from datetime import date
def update_cumulative_ledger_partyledger(instance, entry_date, journal_entry):
    ledger = CumulativeLedger.objects.filter(ledger=instance).last()
    if ledger :
        total_value = ledger.total_value
    else:
        total_value = Decimal(0.0)
    value_changed = instance.total_value - total_value
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        if value_changed > 0:
                CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal = journal_entry)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal = journal_entry)
    else:
        if value_changed > 0:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal = journal_entry)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal = journal_entry)




    

