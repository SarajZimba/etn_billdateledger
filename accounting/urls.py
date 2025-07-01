from django.urls import path
from .views import AccountChartList,AccountChartDetail,AccountChartCreate, end_fiscal_year

urlpatterns = [
path('accountchart/', AccountChartList.as_view(), name='accountchart_list'),
path('accountchart/<int:pk>/', AccountChartDetail.as_view(), name='accountchart_detail'),
path('accountchart/create/', AccountChartCreate.as_view(), name='accountchart_create'),
path('end-fiscal-year/', end_fiscal_year, name='end_fiscal_year')
# path('accountchart/<int:pk>/update/', AccountChartUpdate.as_view(), name='accountchart_update'),
# path('accountchart/delete', AccountChartDelete.as_view(), name='accountchart_delete'),
]

from .views import AccountLedgerList,AccountLedgerDetail,AccountLedgerCreate,AccountLedgerUpdate,AccountLedgerDelete
urlpatterns += [
path('accountledger/', AccountChartList.as_view(), name='accountledger_list'),
path('accountledger/<int:pk>/', AccountLedgerDetail.as_view(), name='accountledger_detail'),
path('accountledger/create/', AccountLedgerCreate.as_view(), name='accountledger_create'),
path('accountledger/<int:pk>/update/', AccountLedgerUpdate.as_view(), name='accountledger_update'),
path('accountledger/delete/<int:pk>', AccountLedgerDelete.as_view(), name='accountledger_delete'),
]

from .views import AccountSubLedgerCreate, AccountSubLedgerUpdate
urlpatterns += [
    path('accountsubledger/create/', AccountSubLedgerCreate.as_view(), name="subledger_create"),
    path('accountsubledger/<int:pk>/update/', AccountSubLedgerUpdate.as_view(), name="subledger_update"),
]

from .views import ExpenseList,ExpenseDetail,ExpenseCreate,ExpenseUpdate,ExpenseDelete
urlpatterns += [
    path('expenses/', ExpenseList.as_view(), name='expenses_list'),
    path('expenses/<int:pk>/', ExpenseDetail.as_view(), name='expenses_detail'),
    path('expenses/create/', ExpenseCreate.as_view(), name='expenses_create'),
    # path('expense/<int:pk>/update/', ExpenseUpdate.as_view(), name='expense_update'),
    path('expense/delete/<int:pk>', ExpenseDelete.as_view(), name='expense_delete'),
]

from .views import JournalEntryCreateView, JournalEntryView,  TrialBalanceView, ProfitAndLoss, BalanceSheet, DepreciationView, PartyLedgerView, LedgerDetailView, PartyLedgerJournalView, PartyLedgerJournal1View, SundryDebtorsLedgersView, SundryCreditorsLedgersView, JournalEntryUpdateView, ExportTrialBalance, export_profit_and_loss_to_excel
from . import views
urlpatterns += [
    path('journal/', JournalEntryView.as_view(), name="journal_list"),
    path('journal/<int:pk>/', JournalEntryView.as_view(), name="journal_detail"),
    path('journal-create/', JournalEntryCreateView.as_view(), name="journal_create"),
    path('trial-balance/', TrialBalanceView.as_view(), name="trial_balance_view"),
    path('pl/', ProfitAndLoss.as_view(), name="pl_view"),
    path('balance-sheet/', BalanceSheet.as_view(), name="balance_sheet_view"),
    path('depreciation/', DepreciationView.as_view(), name="depreciation_view"),
    path('party-ledgers/', PartyLedgerView.as_view(), name="partyledger_view"),
    path('ledger_detail/<int:ledger_id>/', LedgerDetailView.as_view(), name="ledger_detail"),
    path('partyledger_journal/<int:ledger_id>/', PartyLedgerJournalView.as_view(), name="partyledger_journal"),
    path('partyledger_journal1/<int:ledger_id>/', PartyLedgerJournal1View.as_view(), name="partyledger_journal1"),
    path('sundry_debtors_ledgers/', SundryDebtorsLedgersView.as_view(), name='sundry_debtors_ledgers'),
    path('sundry_creditors_ledgers/', SundryCreditorsLedgersView.as_view(), name='sundry_creditors_ledgers'),
    path('journal/<int:journal_id>/soft-delete/', views.soft_delete_journal, name='soft_delete_journal'),
    path('journalentry/<int:pk>/edit/', JournalEntryUpdateView.as_view(), name='edit_journal'),
    path('export-trial-balance/', ExportTrialBalance.as_view(), name="export_trial_balance"),   
    path('export_profit_and_loss/', export_profit_and_loss_to_excel, name='export_profit_and_loss'),


]

from .views import EditOpeningCountView

urlpatterns += [
    # Other URL patterns
    path('edit_opening_count/<int:ledger_id>/', EditOpeningCountView.as_view(), name='edit_opening_count'),
]