from pyBSDate import convert_AD_to_BS
from datetime import datetime


def get_fiscal_year():
    from organization.models import Organization
    org = Organization.objects.first()
    return org.get_fiscal_year()


def calculate_depreciation(amount, percentage, bill_date):
    date_format = '%Y-%m-%d'
    ad_date = datetime.strptime(str(bill_date), date_format)
    year, month, day = ad_date.year, ad_date.month, ad_date.day
    bs_date = convert_AD_to_BS(year, month, day)
    nepali_month_int = bs_date[1]
    depreciation_amount = 0
    amount= float(amount)
    if nepali_month_int <= 3:
        depreciation_amount = (amount*(percentage/100))/3
    elif nepali_month_int <= 9:
        depreciation_amount = amount*(percentage/100)
    else:
        depreciation_amount = (amount*(percentage/100))*2/3
    return depreciation_amount, bs_date


class ProfitAndLossData():

    @staticmethod
    def get_data(revenues, expenses):
        revenue_list= []
        revenue_total = 0
        expense_list= []
        expense_total = 0

        for revenue in revenues:
            revenue_list.append({'title':revenue.ledger_name, 'amount': revenue.total_value})
            revenue_total += revenue.total_value

        for expense in expenses:
            expense_list.append({'title':expense.ledger_name, 'amount': expense.total_value})
            expense_total += expense.total_value

        return expense_list, expense_total, revenue_list, revenue_total
    
"""
Signal to update Cumulative Ledger
"""


from datetime import date
# Though this name is create . It is upadting the ledger entries because the ledger are already created in the cumulative ledger before the journal entries are made 
# def update_cumulative_ledger_journal(journal, data):
def create_cumulative_ledger_journal(instance, journal):
    from .models import CumulativeLedger


    ledger = CumulativeLedger.objects.filter(ledger=instance).last()

    if ledger:
        total_value = ledger.total_value
    else:
        total_value = Decimal(0.0)
    value_changed = instance.total_value - total_value
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        if value_changed > 0:
                CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance,journal=journal)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, journal=journal)
    else:
        if value_changed > 0:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, journal=journal)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, journal=journal)

def sub_below_cumulative_entries(ledger, value_changed, id):
    from .models import CumulativeLedger
    entries_after_id = CumulativeLedger.objects.filter(ledger=ledger, id__gt=id).order_by('id')

    if entries_after_id:
        for entry in entries_after_id:
            entry.total_value -= value_changed
            entry.save()

def add_below_cumulative_entries(ledger, value_changed, id):
    from .models import CumulativeLedger
    entries_after_id = CumulativeLedger.objects.filter(ledger=ledger, id__gt=id).order_by('id')

    if entries_after_id:
        for entry in entries_after_id:
            entry.total_value += value_changed
            entry.save()

def get_subledger(subledger, ledger):
    from .models import AccountSubLedger
    subled = None
    if not subledger.startswith('-'):

        subledger_id = int(subledger)
        subled = AccountSubLedger.objects.get(pk=subledger_id)

    return subled

from decimal import Decimal
from django.db.models import Q
def update_cumulative_ledger_journal(journal, data):
    from .models import CumulativeLedger, AccountLedger, AccountSubLedgerTracking

    journal_entry = journal
    debit_ledgers = data.getlist('debit_ledger', [])
    debit_subledgers = data.getlist('debit_subledger', [])
    debit_amounts = data.getlist('debit_amount', [])
    credit_ledgers = data.getlist('credit_ledger', [])
    credit_subledgers = data.getlist('credit_subledger', [])
    credit_amounts = data.getlist('credit_amount', [])
    print(debit_subledgers)
    print(credit_subledgers)
    entries = CumulativeLedger.objects.filter(journal=journal_entry)
    if entries:

        debit_entries = entries.filter(~Q(debit_amount=0) and Q(credit_amount=0))
        credit_entries = entries.filter(Q(debit_amount=0) and ~Q(credit_amount=0))

    
    for i in range(len(debit_ledgers)):
        debit_ledger_id = int(debit_ledgers[i])
        debit_ledger = AccountLedger.objects.get(pk=debit_ledger_id)
        # debit_particular = debit_particulars[i]
        debit_amount = debit_amounts[i]
        subledger = get_subledger(debit_subledgers[i], debit_ledger)  # Implement your subledger utility function
        debit_ledger_type = debit_ledger.account_chart.account_type

        print(debit_ledger_id)
        print(debit_ledger)
        print(debit_ledger_type)
        if subledger:
                # subledger.total_value -= credit_amount
                accountsubtracking = AccountSubLedgerTracking.objects.get(subledger=subledger, journal=journal_entry)
                prev_amt = accountsubtracking.new_amount
                new_amt = Decimal(debit_amount)
                value_changed = prev_amt - new_amt
                previous_accountsubtracking = AccountSubLedgerTracking.objects.filter(
                    subledger=subledger,
                    created_at__lt=accountsubtracking.created_at
                ).order_by('-created_at').first()  # Get the latest previous object
                accountsubtracking.prev_amount = previous_accountsubtracking.new_amount
                accountsubtracking.new_amount = new_amt
                accountsubtracking.value_changed = new_amt
                accountsubtracking.save()
        debit_entry = debit_entries.filter(ledger=debit_ledger)
        new_debit_amount = Decimal(debit_amount)
        for entry in debit_entry:
            previous_debitamount = entry.debit_amount
            print(f" prev debit {previous_debitamount}")
            diff = previous_debitamount - new_debit_amount

            entry.debit_amount = new_debit_amount
            print(f"new debit amount {new_debit_amount}")
            entry.value_changed = new_debit_amount
            if previous_debitamount >= new_debit_amount:
                entry.total_value -= diff
                sub_below_cumulative_entries(entry.ledger, diff, entry.id)
            else:
                entry.total_value += abs(diff)
                add_below_cumulative_entries(entry.ledger, abs(diff), entry.id)

            entry.save()

    for i in range(len(credit_ledgers)):
        credit_ledger_id = int(credit_ledgers[i])
        credit_ledger = AccountLedger.objects.get(pk=credit_ledger_id)
        # credit_particular = credit_particulars[i]
        credit_amount = credit_amounts[i]
        subledger = get_subledger(credit_subledgers[i], credit_ledger)  # Implement your subledger utility function
        credit_ledger_type = credit_ledger.account_chart.account_type
        print(credit_ledger_id)
        print(credit_ledger)
        print(credit_ledger_type)


        if subledger:
                # subledger.total_value -= credit_amount
                accountsubtracking = AccountSubLedgerTracking.objects.get(subledger=subledger, journal=journal_entry)
                prev_amt = accountsubtracking.new_amount
                new_amt = Decimal(credit_amount)
                value_changed = prev_amt - new_amt
                previous_accountsubtracking = AccountSubLedgerTracking.objects.filter(
                    subledger=subledger,
                    created_at__lt=accountsubtracking.created_at
                ).order_by('-created_at').first()  # Get the latest previous object
                accountsubtracking.prev_amount = previous_accountsubtracking.new_amount
                accountsubtracking.new_amount = new_amt
                accountsubtracking.value_changed = new_amt
                accountsubtracking.save()


        credit_entry = credit_entries.filter(ledger=credit_ledger)
        for entry in credit_entry:
            previous_creditamount = entry.credit_amount
            new_credit_amount = Decimal(credit_amount)
            diff = previous_creditamount - new_credit_amount
            entry.credit_amount = new_credit_amount
            entry.value_changed = new_credit_amount
            if previous_creditamount >= new_credit_amount:
                entry.total_value -= diff

                sub_below_cumulative_entries(entry.ledger, diff, entry.id)
                # entries_before_id = CumulativeLedger.objects.filter(ledger=entry.ledger, id__lt=entry.id).order_by('id')
                # if entries_before_id:
                #     last_entry_before_updatedobject = entries_before_id.last()
                #     last_objectvalue_before_update = last_entry_before_updatedobject.total_value
                #     entry.total_value += last_objectvalue_before_update
            else:
                entry.total_value += abs(diff)
                add_below_cumulative_entries(entry.ledger, abs(diff), entry.id)
                # entries_before_id = CumulativeLedger.objects.filter(ledger=entry.ledger, id__lt=entry.id).order_by('id')
                # if entries_before_id:
                #     last_entry_before_updatedobject = entries_before_id.last()
                #     last_objectvalue_before_update = last_entry_before_updatedobject.total_value
                #     entry.total_value += last_objectvalue_before_update
            entry.save()
    print(data)


# def add_below_cumulative_entries(ledger, value_changed, id):
#     from .models import CumulativeLedger
#     entries_after_id = CumulativeLedger.objects.filter(ledger=ledger, id__gt=id).order_by('id')

#     if entries_after_id:
#         for entry in entries_after_id:
#             entry.total_value += value_changed
#             entry.save()

def get_subledger_from_journal(journal_entry):
    from .models import TblCrJournalEntry, TblDrJournalEntry

    credit_entries = TblCrJournalEntry.objects.filter(journal_entry=journal_entry)
    debit_entries = TblDrJournalEntry.objects.filter(journal_entry=journal_entry)

    subledgers = {
        "credit_subledgers" : [],
        "debit_subledgers" : []
    }
    # subledgers = {
    #     "credit_subledgers" : [],
    #     "debit_subledgers" : []
    # }
    for entry in credit_entries:

        if entry.sub_ledger:
            subledger_dict = {
                "subledger":entry.sub_ledger.id,
                "value": entry.credit_amount,
                "ledger": entry.ledger.id,
                "journal": entry.journal_entry
            }

            subledgers['credit_subledgers'].append(subledger_dict)

    for entry in debit_entries:

        if entry.sub_ledger:
            subledger_dict = {
                "subledger":entry.sub_ledger.id,
                "value": entry.debit_amount,
                "ledger": entry.ledger.id,
                "journal": entry.journal_entry
            }

            subledgers['debit_subledgers'].append(subledger_dict)

    return subledgers

        # subledgers

def adjust_cumulative_ledger_afterentries(journal_entry):
    from .models import CumulativeLedger, AccountSubLedgerTracking, AccountSubLedger, AccountLedger
    entries = CumulativeLedger.objects.filter(journal=journal_entry)
    
    subledgers_of_this_journal = get_subledger_from_journal(journal_entry)

    for subledger in subledgers_of_this_journal['credit_subledgers']:
        accountsubledger = AccountSubLedger.objects.get(pk=subledger['subledger'])
        ledger = AccountLedger.objects.get(pk=subledger['ledger'])

        value = subledger['value']

        journal = subledger['journal']

        ledger_type = ledger.account_chart.account_type

        if ledger_type in ['Asset', 'Expense']:
            accountsubledger.total_value += value
            accountsubledger.save()
        elif ledger_type in ['Liability', 'Revenue', 'Equity']:
            accountsubledger.total_value -= value
            accountsubledger.save()


    for subledger in subledgers_of_this_journal['debit_subledgers']:
        accountsubledger = AccountSubLedger.objects.get(pk=subledger['subledger'])
        ledger = AccountLedger.objects.get(pk=subledger['ledger'])

        value = subledger['value']

        journal = subledger['journal']

        ledger_type = ledger.account_chart.account_type

        if ledger_type in ['Asset', 'Expense']:
            accountsubledger.total_value -= value
            accountsubledger.save()
        elif ledger_type in ['Liability', 'Revenue', 'Equity']:
            accountsubledger.total_value += value
            accountsubledger.save()



    if entries:

        debit_entries = entries.filter(~Q(debit_amount=0) and Q(credit_amount=0))
        credit_entries = entries.filter(Q(debit_amount=0) and ~Q(credit_amount=0))
        print(debit_entries)
        print(credit_entries)

    for entry in debit_entries:

        id = entry.id
        value_changed = entry.value_changed
        if value_changed < 0:
            add_below_cumulative_entries(entry.ledger, abs(value_changed), entry.id)
        else:
            sub_below_cumulative_entries(entry.ledger, abs(value_changed), entry.id)

    for entry in credit_entries:

        id = entry.id
        value_changed = entry.value_changed
        if value_changed < 0:
            add_below_cumulative_entries(entry.ledger, abs(value_changed), entry.id)
        else:
            sub_below_cumulative_entries(entry.ledger, abs(value_changed), entry.id)

    subledgertracking = AccountSubLedgerTracking.objects.filter(journal=journal_entry)
    subledgertracking.delete()
