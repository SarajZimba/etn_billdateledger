from accounting.models import AccountLedger, AccountSubLedger
from purchase.models import AccountProductTracking

def create_subledgers_after_product_create(product):
    ledger = AccountLedger.objects.get(ledger_name="Inventory Purchases")
    subledgername = f'{product.title} ({product.category.title})'
    total = product.cost_price * product.opening_count
    try:
        sub = AccountSubLedger.objects.get(sub_ledger_name=subledgername, ledger=ledger)
        sub.total_value += total
        sub.save()
    except AccountSubLedger.DoesNotExist:
        AccountSubLedger.objects.create(sub_ledger_name=subledgername, ledger=ledger, total_value=total)
    AccountProductTracking.objects.create(product=product, purchase_rate=product.cost_price, quantity=product.opening_count, remaining_stock=product.opening_count)

from organization.models import Branch
from product.models import BranchStockTracking
def check_opening_for_branch():

    branches = Branch.objects.filter(status=True, is_deleted=False)

    branch_status_list = []
    for branch in branches:
         
        has_stock_entries = BranchStockTracking.objects.filter(branch=branch).exists()

        branch_status_list.append({
            'branch': branch,
            'has_stock_entries': has_stock_entries
        })

    return branch_status_list