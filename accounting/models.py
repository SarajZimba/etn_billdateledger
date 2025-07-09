from typing import Iterable, Optional
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounting.utils import get_fiscal_year
from django.db.models.signals import pre_delete

    
class AccountBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AccountChart(AccountBaseModel):
    account_type = models.CharField(max_length=100)
    group = models.CharField(max_length=100, unique=True)
    is_editable = models.BooleanField(default=True)

    def __str__(self):
        return self.group
    
class AccountLedger(AccountBaseModel):
    account_chart = models.ForeignKey(AccountChart, on_delete=models.CASCADE)
    ledger_name = models.CharField(max_length=200, unique=True)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_editable = models.BooleanField(default=True)
    opening_count = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    def __str__(self):
        return self.ledger_name

class AccountSubLedger(AccountBaseModel):
    ledger = models.ForeignKey(AccountLedger, on_delete=models.CASCADE, null=True, blank=True)
    sub_ledger_name = models.CharField(max_length=100)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_editable = models.BooleanField(default=True)

    def __str__(self):
        return self.sub_ledger_name
    


class TblJournalEntry(AccountBaseModel):
    employee_name = models.CharField(max_length=100, null=True, blank=True)
    journal_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fiscal_year = models.CharField(max_length=10)
    entry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return 'Journal Entry'

class CumulativeLedger(AccountBaseModel):
    account_chart = models.ForeignKey(AccountChart, on_delete=models.PROTECT)
    ledger_name = models.CharField(max_length=200)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    value_changed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    debit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ledger = models.ForeignKey(AccountLedger, models.CASCADE, null=True, blank=True)
    journal = models.ForeignKey(TblJournalEntry, models.CASCADE, null=True, blank=True)
    entry_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.ledger_name

class TblCrJournalEntry(AccountBaseModel):
    ledger = models.ForeignKey(AccountLedger, on_delete=models.PROTECT, related_name='credit_entries')
    sub_ledger = models.ForeignKey(AccountSubLedger, null=True, on_delete=models.SET_NULL)
    journal_entry = models.ForeignKey(TblJournalEntry, on_delete=models.CASCADE)
    particulars = models.TextField(max_length=255)
    credit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paidfrom_ledger = models.ForeignKey(AccountLedger, on_delete=models.PROTECT, null=True, related_name='credit_entries_paidfrom')

    
    def __str__(self):
        return f'{self.ledger} -> {self.credit_amount}'


class TblDrJournalEntry(AccountBaseModel):
    ledger = models.ForeignKey(AccountLedger, on_delete=models.PROTECT, related_name='debit_entries')
    sub_ledger = models.ForeignKey(AccountSubLedger, null=True, on_delete=models.SET_NULL)
    journal_entry = models.ForeignKey(TblJournalEntry, on_delete=models.CASCADE)
    particulars = models.TextField(max_length=255)
    debit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paidfrom_ledger = models.ForeignKey(AccountLedger, on_delete=models.PROTECT, null=True, related_name='debit_entries_paidfrom')


    def __str__(self):
        return f'{self.ledger} -> {self.debit_amount}'


class Expense(AccountBaseModel):
    ledger = models.ForeignKey(AccountLedger, related_name='ledger',  on_delete=models.PROTECT)
    sub_ledger = models.ForeignKey(AccountSubLedger, on_delete=models.PROTECT, null=True, blank=True)
    credit_ledger = models.ForeignKey(AccountLedger, related_name='credit_ledger', on_delete=models.PROTECT)
    credit_sub_ledger = models.ForeignKey(AccountSubLedger, related_name='credit_sub_ledger', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.PositiveIntegerField()
    description = models.CharField(max_length=255)
    journal = models.ForeignKey(TblJournalEntry, models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Expense @ {self.amount}"
    
# @receiver(post_save, sender=Expense)
# def create_journal_for_expense(sender, instance, created, **kwargs):
#     from bill.utils import update_cumulative_ledger_bill
#     if created:
    
#         journal = TblJournalEntry.objects.create(employee_name="From expense form", journal_total=instance.amount)
#         TblDrJournalEntry.objects.create(ledger=instance.ledger, debit_amount=instance.amount, particulars=f"Automatic: {instance.ledger.ledger_name} a/c Dr", journal_entry=journal)
#         TblCrJournalEntry.objects.create(ledger=instance.credit_ledger, credit_amount=instance.amount, particulars=f"Automatic: To {instance.credit_ledger.ledger_name}", journal_entry=journal)
#         instance.ledger.total_value += instance.amount
#         instance.ledger.save()
#         update_cumulative_ledger_bill(instance.ledger)
#         # if instance.sub_ledger:
#         #     instance.sub_ledger.total_value += instance.amount
#         #     instance.sub_ledger.save()

#         instance.credit_ledger.total_value -= instance.amount
#         instance.credit_ledger.save()
#         update_cumulative_ledger_bill(instance.credit_ledger)


    
class FiscalYearSubLedger(AccountBaseModel):
    ledger = models.ForeignKey(AccountLedger, on_delete=models.PROTECT)
    sub_ledger_name = models.CharField(max_length=100)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_editable = models.BooleanField(default=True)
    fiscal_year = models.CharField(max_length=10)

    class Meta:
        unique_together = 'sub_ledger_name', 'fiscal_year'

    def __str__(self):
        return self.sub_ledger_name

    def save(self, *args, **kwargs):
        self.fiscal_year = get_fiscal_year()
        super().save(*args, **kwargs)


from purchase.models import AssetPurchaseItem

class Depreciation(AccountBaseModel):
    item = models.ForeignKey(AssetPurchaseItem, on_delete=models.CASCADE)
    miti = models.CharField(max_length=15)
    depreciation_amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fiscal_year = models.CharField(max_length=15, null=True)
    ledger = models.ForeignKey(AccountLedger, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "Depreciation"
    
    def save(self, *args, **kwargs):
        self.fiscal_year = get_fiscal_year()
        super().save(*args, **kwargs)
    

class FiscalYearLedger(AccountBaseModel):
    account_chart = models.ForeignKey(AccountChart, on_delete=models.PROTECT)
    ledger_name = models.CharField(max_length=200)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_editable = models.BooleanField(default=True)
    fiscal_year = models.CharField(max_length=10)

    class Meta:
        unique_together = 'ledger_name', 'fiscal_year'

    def __str__(self):
        return self.ledger_name
    
    def save(self, *args, **kwargs):
        self.fiscal_year = get_fiscal_year()
        super().save(*args, **kwargs)
    



class AccountSubLedgerTracking(AccountBaseModel):
    subledger = models.ForeignKey(AccountSubLedger, models.CASCADE, null=True, blank=True)
    prev_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    value_changed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    journal = models.ForeignKey(TblJournalEntry, models.CASCADE, null=True, blank=True)