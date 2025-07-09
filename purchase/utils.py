from accounting.models import CumulativeLedger
from decimal import Decimal


"""
Signal to update Cumulative Ledger
"""
from datetime import date
def update_cumulative_ledger_purchase(instance, entry_date, journal_entry):
    ledger = CumulativeLedger.objects.filter(ledger=instance).last()
    if ledger :
        total_value = ledger.total_value
    else:
        total_value = Decimal(0.0)
    value_changed = instance.total_value - total_value
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        if value_changed > 0:
                CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal=journal_entry)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal=journal_entry)
    else:
        if value_changed > 0:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date,  journal=journal_entry)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date,  journal=journal_entry)

def create_cumulative_ledger_purchase(instance, entry_date, journal_entry):
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=instance.total_value, ledger=instance, debit_amount=instance.total_value, entry_date=entry_date, journal=journal_entry)
    else:
        CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=instance.total_value, ledger=instance, credit_amount=instance.total_value, entry_date=entry_date, journal=journal_entry)

from accounting.utils import update_cumulative_ledger_journal
from accounting.models import AccountSubLedgerTracking, TblJournalEntry, AccountLedger, AccountSubLedger, TblDrJournalEntry, TblCrJournalEntry
from django.http import Http404
from decimal import Decimal as D
from django.shortcuts import get_object_or_404
def purchaseupdatejournalandcumulativepaymentmode(posted_data, pk):
    # Define your GET method to display the form for updating a journal entry         

    # def post(self, request, pk):
    data = posted_data
    debit_ledgers = data.getlist('debit_ledger', [])
    debit_particulars = data.getlist('debit_particular', [])
    debit_amounts = data.getlist('debit_amount', [])
    debit_subledgers = data.getlist('debit_subledger', [])

    credit_ledgers = data.getlist('credit_ledger', [])
    credit_particulars = data.getlist('credit_particular', [])
    credit_amounts = data.getlist('credit_amount', [])
    credit_subledgers = data.getlist('credit_subledger', [])
        # entry_date = data.get('entry_date')
        # narration = data.get('narration')

    ledgers = AccountLedger.objects.all()
    sub_ledgers = AccountSubLedger.objects.all()

    try:
        parsed_debitamt = [D(i) for i in debit_amounts]
        parsed_creditamt = [D(i) for i in credit_amounts]
    except Exception:
        pass
        # messages.error(request, "Please Enter a valid amount")
        # return render(request, 'accounting/journal/journal_entry_update.html', {'ledgers': ledgers, 'sub_ledgers': sub_ledgers})

    debit_sum, credit_sum = sum(parsed_debitamt), sum(parsed_creditamt)
    if debit_sum != credit_sum:
        pass

    for dr in debit_ledgers:
        if dr.startswith('-'):
            # messages.error(request, "Ledger must be selected")
            # return render(request, 'accounting/journal/journal_entry_update.html', {'ledgers': ledgers, 'sub_ledgers': sub_ledgers})
            pass
    # Retrieve the journal_entry object or raise a 404 error if not found
    try:
        journal_entry = TblJournalEntry.objects.get(pk=pk)
    except TblJournalEntry.DoesNotExist:
        raise Http404("Journal Entry does not exist")

    update_cumulative_ledger_journal(journal_entry, data)


    #Update the value of ledger of old entries
    existing_credit_entriess = TblCrJournalEntry.objects.filter(journal_entry=journal_entry)
    print("credit_entries", existing_credit_entriess)
    for existing_credit_entries in existing_credit_entriess:
        old_credit_ledger = existing_credit_entries.ledger if existing_credit_entries else None
        old_credit_subledger = existing_credit_entries.sub_ledger if existing_credit_entries else None
        print("credit_name", old_credit_ledger.ledger_name)
        old_credit_ledger_type = old_credit_ledger.account_chart.account_type
        old_credit_amount = existing_credit_entries.credit_amount
        if old_credit_ledger_type in ['Asset', 'Expense']:
            print("to be increased", old_credit_amount)
            old_credit_ledger.total_value += old_credit_amount
            old_credit_ledger.save()
            if old_credit_subledger:
                old_credit_subledger.total_value += old_credit_amount
                old_credit_subledger.save()
                    # subledgertracking = AccountSubLedgerTracking.objects.filter(subledger=old_credit_subledger, journal=journal_entry)

        elif old_credit_ledger_type in ['Liability', 'Revenue', 'Equity']:
            print("to be decreased", old_credit_amount)
            old_credit_ledger.total_value -= old_credit_amount
            old_credit_ledger.save()
            if old_credit_subledger:
                old_credit_subledger.total_value -= old_credit_amount
                old_credit_subledger.save()

        # Update or create credit entries

    credit_to_debit_mapping = {}
    for i in range(len(credit_ledgers)):
        credit_ledger_id = int(credit_ledgers[i])
        credit_ledger = AccountLedger.objects.get(pk=credit_ledger_id)
        credit_particular = credit_particulars[i]
        credit_amount = parsed_creditamt[i]
        subledger = get_subledger(credit_subledgers[i], credit_ledger)  # Implement your subledger utility function
        credit_ledger_type = credit_ledger.account_chart.account_type
            
        # Check if there is an existing entry for this ledger, if so, update it, otherwise, create a new one
        existing_entry = existing_credit_entriess.filter(ledger=credit_ledger).first()

        if existing_entry:  
            existing_entry.particulars = credit_particular
            existing_entry.credit_amount = credit_amount
            existing_entry.sub_ledger = subledger
            existing_entry.paidfrom_ledger = credit_ledger
            existing_entry.save()
        else:
            TblCrJournalEntry.objects.create(
                ledger=credit_ledger,
                journal_entry=journal_entry,
                particulars=credit_particular,
                credit_amount=credit_amount,
                sub_ledger=subledger,
                paidfrom_ledger=credit_ledger
            )

        if credit_ledger_type in ['Asset', 'Expense']:
            credit_ledger.total_value -= credit_amount
            credit_ledger.save()
            if subledger:
                subledger.total_value -= credit_amount
                subledger.save()
        elif credit_ledger_type in ['Liability', 'Revenue', 'Equity']:
            credit_ledger.total_value += credit_amount
            credit_ledger.save()
            if subledger:

                subledger.total_value += credit_amount
                subledger.save()



    #Update the value of ledger of old entries
    existing_debit_entriess = TblDrJournalEntry.objects.filter(journal_entry=journal_entry)
    print("debit_entries", existing_debit_entriess)
    for existing_debit_entries in existing_debit_entriess:
        old_debit_ledger = existing_debit_entries.ledger if existing_debit_entries else None
        old_debit_subledger = existing_debit_entries.sub_ledger if existing_debit_entries else None
        print("debit_name", old_debit_ledger.ledger_name)
        old_debit_ledger_type = old_debit_ledger.account_chart.account_type
        old_debit_amount = existing_debit_entries.debit_amount
        if old_debit_ledger_type in ['Asset', 'Expense']:
            print("to be increased", old_debit_amount)
            old_debit_ledger.total_value -= old_debit_amount
            old_debit_ledger.save()
            if old_debit_subledger:
                old_debit_subledger.total_value -= old_debit_amount
                old_debit_subledger.save()
        elif old_debit_ledger_type in ['Liability', 'Revenue', 'Equity']:
            print("to be decreased", old_debit_amount)
            old_debit_ledger.total_value += old_debit_amount
            old_debit_ledger.save()
            if old_debit_subledger:
                old_debit_subledger.total_value += old_debit_amount
                old_debit_subledger.save()

    # Delete any existing entries that are no longer present in the form
    existing_credit_entriess.exclude(ledger__id__in=credit_ledgers).delete()

    # Update or create debit entries
    # existing_debit_entries = TblDrJournalEntry.objects.filter(journal_entry=journal_entry)
    for i in range(len(debit_ledgers)):
        debit_ledger_id = int(debit_ledgers[i])
        debit_ledger = AccountLedger.objects.get(pk=debit_ledger_id)
        debit_particular = debit_particulars[i]
        debit_amount = parsed_debitamt[i]
        subledger = get_subledger(debit_subledgers[i], debit_ledger)  # Implement your subledger utility function
        debit_ledger_type = debit_ledger.account_chart.account_type
            
        # Check if there is an existing entry for this ledger, if so, update it, otherwise, create a new one
        existing_entry = existing_debit_entriess.filter(ledger=debit_ledger).first()
        if existing_entry:
            existing_entry.particulars = debit_particular
            existing_entry.debit_amount = debit_amount
            existing_entry.sub_ledger = subledger
            existing_entry.paidfrom_ledger = credit_to_debit_mapping.get(credit_ledger)
            existing_entry.save()
        else:
            TblDrJournalEntry.objects.create(
                ledger=debit_ledger,
                journal_entry=journal_entry,
                particulars=debit_particular,
                debit_amount=debit_amount,
                sub_ledger=subledger,
                paidfrom_ledger=credit_to_debit_mapping.get(credit_ledger)
                )

        if debit_ledger_type in ['Asset', 'Expense']:
            debit_ledger.total_value += debit_amount
            debit_ledger.save()
            if subledger:
                subledger.total_value += debit_amount
                subledger.save()
        elif debit_ledger_type in ['Liability', 'Revenue', 'Equity']:
            debit_ledger.total_value -= debit_amount
            debit_ledger.save()
            if subledger:
                subledger.total_value -= debit_amount
                subledger.save()


    existing_debit_entriess.exclude(ledger__id__in=debit_ledgers).delete()

    # Update journal entry data
    # journal_entry.employee_name = request.user.username
    journal_entry.employee_name = "admin"
    journal_entry.journal_total = debit_sum
    # journal_entry.entry_date = entry_date
    # journal_entry.narration = narration
    journal_entry.save()


def get_subledger(self, subledger, ledger):
    subled = None
    if not subledger.startswith('-'):
        try:
            subledger_id = int(subledger)
            subled = AccountSubLedger.objects.get(pk=subledger_id)
        except ValueError:
            subled = AccountSubLedger.objects.create(sub_ledger_name=subledger, is_editable=True, ledger=ledger)
    return subled


from accounting.utils import adjust_cumulative_ledger_afterentries
def soft_delete_journal(request, journal_id):
    try:
        # Retrieve the journal entry or return a 404 if it doesn't exist
        journal_entry = get_object_or_404(TblJournalEntry, id=journal_id)

        # Get related credit and debit entries
        credit_entries = TblCrJournalEntry.objects.filter(journal_entry=journal_entry)
        debit_entries = TblDrJournalEntry.objects.filter(journal_entry=journal_entry)

        # Reverse the ledger operations for credit entries
        for credit_entry in credit_entries:
            ledger = credit_entry.ledger
            ledger_type = ledger.account_chart.account_type

            # Reverse the operation based on ledger type
            if ledger_type in ['Asset', 'Expense']:
                ledger.total_value += credit_entry.credit_amount
            elif ledger_type in ['Liability', 'Revenue', 'Equity']:
                ledger.total_value -= credit_entry.credit_amount

            ledger.save()
            # update_cumulative_ledger_bill(ledger)

        # Reverse the ledger operations for debit entries
        for debit_entry in debit_entries:
            ledger = debit_entry.ledger
            ledger_type = ledger.account_chart.account_type

            # Reverse the operation based on ledger type
            if ledger_type in ['Asset', 'Expense']:
                ledger.total_value -= debit_entry.debit_amount
            elif ledger_type in ['Liability', 'Revenue', 'Equity']:
                ledger.total_value += debit_entry.debit_amount

            ledger.save()
            # update_cumulative_ledger_bill(ledger)
        adjust_cumulative_ledger_afterentries(journal_entry)
 
        journal_entry.delete()







    except TblJournalEntry.DoesNotExist:
        # Handle the case where the journal entry doesn't exist.
        # messages.error(request, "Journal Entry not found.")
        pass
    except Exception as e:
        # Handle any other exceptions or errors as needed
        # messages.error(request, f"An error occurred: {str(e)}")
        pass

    return True