from django import forms
from root.forms import BaseForm
from .models import AccountChart, AccountLedger, TblDrJournalEntry, TblCrJournalEntry, AccountSubLedger, Expense, TblJournalEntry
from django.db.models import Q

class AccountChartForm(BaseForm, forms.ModelForm):
    class Meta:
        model = AccountChart
        exclude = 'is_editable',
     

class AccountLedgerForm(BaseForm, forms.ModelForm):
    
    class Meta:
        model = AccountLedger
        exclude = 'is_editable', 'opening_count'
   


        

class AccountSubLedgerForm(BaseForm, forms.ModelForm):
    class Meta:
        model = AccountSubLedger
        exclude = 'is_editable',
 


# class ExpenseForm(BaseForm, forms.ModelForm):
#     class Meta:
#         model = Expense
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields["credit_ledger"] = forms.ModelChoiceField( queryset=AccountLedger.objects.filter(account_chart=AccountChart.objects.filter(group="Liquid Asset").first()))
#         self.fields["ledger"] = forms.ModelChoiceField( queryset=AccountLedger.objects.filter(~Q(ledger_name='Inventory Expenses'), account_chart__in=AccountChart.objects.filter(account_type="Expense")))
#         self.fields["sub_ledger"] = forms.ModelChoiceField(queryset=AccountSubLedger.objects.filter(~Q(ledger__ledger_name='Inventory Expenses'),ledger__in=AccountLedger.objects.filter(account_chart__in=AccountChart.objects.filter(account_type="Expense"))))

#         self.fields["credit_ledger"].widget.attrs = {
#             "class":"form-select",
#             "data-control": "select2",
#             "data-placeholder": "Paid From",
#         }
#         self.fields["ledger"].widget.attrs = {
#             "class":"form-select",
#             "data-control": "select2",
#             "data-placeholder": "Expense from",
#         }
#         self.fields["sub_ledger"].widget.attrs = {
#             "class":"form-select",
#             "data-control": "select2",
#             "data-placeholder": "Select Sub Ledger",
#         }
#         self.fields["sub_ledger"].required = False
class ExpenseForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Expense
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["credit_ledger"] = forms.ModelChoiceField( queryset=AccountLedger.objects.filter(account_chart=AccountChart.objects.filter(group="Liquid Asset").first()))
        self.fields["ledger"] = forms.ModelChoiceField( queryset=AccountLedger.objects.filter(~Q(ledger_name='Inventory Expenses'), account_chart__in=AccountChart.objects.filter(account_type="Expense")))
        self.fields["sub_ledger"] = forms.ModelChoiceField(queryset=AccountSubLedger.objects.filter(~Q(ledger__ledger_name='Inventory Expenses'),ledger__in=AccountLedger.objects.filter(account_chart__in=AccountChart.objects.filter(account_type="Expense"))))

        self.fields["credit_ledger"].widget.attrs = {
            "class":"form-select",
            "data-control": "select2",
            "data-placeholder": "Paid From",
        }
        self.fields["ledger"].widget.attrs = {
            "class":"form-select",
            "data-control": "select2",
            "data-placeholder": "Expense from",
        }
        self.fields["sub_ledger"].widget.attrs = {
            "class":"form-select",
            "data-control": "select2",
            "data-placeholder": "Select Sub Ledger",
        }


class DrJournalEntryForm(BaseForm, forms.ModelForm):
    employee_name = forms.CharField(required=False)
    class Meta:
        model = TblDrJournalEntry
        fields = '__all__'


class CrJournalEntryForm(BaseForm, forms.ModelForm):
    class Meta:
        model = TblCrJournalEntry
        fields = '__all__'
        

class JournalEntryForm(forms.Form):
    debit_ledger = forms.ModelChoiceField(queryset=AccountLedger.objects.all())
    debit_particulars = forms.CharField(max_length=255)
    debit_amount = forms.FloatField(initial=0,)

    credit_ledger = forms.ModelChoiceField(queryset=AccountLedger.objects.all())
    credit_particulars = forms.CharField(max_length=255)
    credit_amount = forms.FloatField(initial=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["debit_ledger"].widget.attrs["class"] = 'form-select'
        self.fields["debit_ledger"].widget.attrs["data-control"] = 'select2'

        self.fields["credit_ledger"].widget.attrs["class"] = 'form-select'
        self.fields["credit_ledger"].widget.attrs["data-control"] = 'select2'


class OpeningCountForm(forms.Form):
    opening_count = forms.FloatField(label='New Opening count')
    


    


