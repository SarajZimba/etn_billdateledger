from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from accounting.models import AccountChart, AccountLedger,TblJournalEntry, AccountSubLedger, CumulativeLedger
from purchase.models import DepreciationPool
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from api.serializers.accounting import JournalEntryModelSerializer, AccountLedgerSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum
from django.forms.models import model_to_dict
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from organization.models import Organization

@api_view(['PUT'])
def update_account_type(request, pk):
    ac = get_object_or_404(AccountChart, pk=pk)
    ac.account_type=request.query_params.get('accountType')
    ac.save()
    return Response({'Message': 'Successful'})

# @api_view(['PUT'])
# def update_account_ledger(request, pk):
#     subledger = get_object_or_404(AccountLedger, pk=pk)
#     subledger.ledger_name = request.data.get('content', subledger.ledger_name)
#     subledger.save()
#     return Response({'Message': 'Successful'})

@api_view(['PUT'])
def update_account_ledger(request, pk):
    ledger = get_object_or_404(AccountLedger, pk=pk)

    cumulativeledgers = CumulativeLedger.objects.filter(ledger_name= ledger.ledger_name)
    ledger.ledger_name = request.data.get('content', ledger.ledger_name)
    print(ledger.ledger_name)
    # print(cumulativeledger)
    for cumulativeledger in cumulativeledgers:
        cumulativeledger.ledger_name = request.data.get('content', cumulativeledger.ledger_name)
        cumulativeledger.save()
    ledger.save()
    return Response({'Message': 'Successful'})

@api_view(['PUT'])
def update_account_group(request, pk):
    ledger = get_object_or_404(AccountChart, pk=pk)
    ledger.group = request.data.get('content', ledger.group)
    ledger.save()
    return Response({'Message': 'Successful'})

@api_view(['PUT'])
def update_account_subledger(request, pk):
    sub_ledger = get_object_or_404(AccountSubLedger, pk=pk)
    sub_ledger.sub_ledger_name = request.data.get('content', sub_ledger.sub_ledger_name)
    sub_ledger.save()
    return Response({'Message': 'Successful'})

@api_view(['GET'])
def get_depreciation_pool(request):
    data = DepreciationPool.objects.all().values()
    return Response({'data':data})


class ChartOfAccountAPIView(APIView):
    def get(self, request):
        data = {}
        org = Organization.objects.all()
        if org:
            o = org.first()
            data['organization'] = {"name":o.org_name, "email":o.company_contact_email, "address": o.company_address}
        account_chart = AccountChart.objects.all()
        for ac in account_chart:
            if ac.account_type not in data:
                data[ac.account_type] = {"groups":[]}
            data[ac.account_type]["groups"].append({"group_name":ac.group, "ledgers":[]})
            for ledger in ac.accountledger_set.all():
                data[ac.account_type]["groups"][-1]['ledgers'].append({"name":ledger.ledger_name, "total_value":ledger.total_value, "sub_ledgers":[]})
                for subl in ledger.accountsubledger_set.all():
                    data[ac.account_type]["groups"][-1]['ledgers'][-1]["sub_ledgers"].append({"name":subl.sub_ledger_name, "value":subl.total_value})

        return Response(data)
    

class JournalEntryAPIView(ListAPIView):
    queryset = TblJournalEntry.objects.all()
    serializer_class = JournalEntryModelSerializer

    def list(self, request, *args, **kwargs):
        from_date = self.request.query_params.get('fromDate')
        to_date = self.request.query_params.get('toDate')
        if from_date and to_date:
            queryset = TblJournalEntry.objects.filter(created_at__range=[from_date, to_date])
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        else:
            queryset = TblJournalEntry.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)


class TrialBalanceAPIView(APIView):

    permission_classes = IsAuthenticated, 

    def get(self, request):
        trial_balance = []
        total = {'debit_total':0, 'credit_total':0}
        ledgers = AccountLedger.objects.filter(total_value__gt=0)
        for led in ledgers:
            data = {}
            data['ledger']=led.ledger_name
            account_type = led.account_chart.account_type
            data['account_head']=account_type

            if account_type in ['Asset', 'Expense']:
                if led.total_value > 0:
                    data['debit'] = led.total_value
                    total['debit_total'] += led.total_value
                    data['credit'] = '-'
                else:
                    data['credit'] = led.total_value
                    total['credit_total'] += led.total_value
                    data['debit'] = '-'
            else:
                if led.total_value > 0:
                    data['credit'] = led.total_value
                    total['credit_total'] += led.total_value
                    data['debit'] = '-'
                else:
                    data['debit'] = led.total_value
                    total['debit_total'] += led.total_value
                    data['credit'] = '-'
            trial_balance.append(data)

        vat_receivable, vat_payable = 0, 0
        for data in trial_balance:
            if data['ledger'] == 'VAT Receivable':
                vat_receivable = data['debit']
                total['debit_total'] -= data['debit']
                trial_balance.remove(data)
            if data['ledger'] == 'VAT Payable':
                vat_payable = data['credit']
                total['credit_total'] -= data['credit']
                trial_balance.remove(data)
        vat_amount = vat_receivable - vat_payable
        if vat_amount > 0:
            trial_balance.append({'ledger':'VAT', 'account_head':'Asset', 'debit':vat_amount, 'credit':'-'})
            total['debit_total'] += vat_amount
        elif vat_amount < 0:
            trial_balance.append({'ledger':'VAT', 'account_head':'Liability', 'debit':'-', 'credit':abs(vat_amount)})
            total['credit_total'] += abs(vat_amount)

        trial_balance = sorted(trial_balance, key=lambda x:x['account_head'])
        context = {
            'trial_balance': trial_balance,
            "total": total
        }
        return Response(context)


class ProfitAndLossAPIView(APIView):

    def get(self, request):
        expense = AccountLedger.objects.filter(account_chart__account_type="Expense")
        income = AccountLedger.objects.filter(account_chart__account_type="Revenue")
        expense_serializer = AccountLedgerSerializer(expense, many=True)
        income_serializer = AccountLedgerSerializer(income, many=True)
        total_income, total_expense = 0, 0

        for income in income_serializer.data:
            total_income += float(income['total_value'])
        
        for expense in expense_serializer.data:
            total_expense += float(expense['total_value'])

        data = {
            "income":income_serializer.data,
            "expense": expense_serializer.data,
            "total_income": total_income,
            "total_expense":total_expense
        }
        return Response(data)
    

class BalanceSheetAPIView(APIView):
    #permission_classes = IsAdminUser,
    def get(self, request):
        print(request.user.is_staff)
        context = {}
        asset_dict = {
            "groups":[]
        }
        liability_dict = {
            "groups": []
        }

        assets = AccountChart.objects.filter(account_type='Asset')
        for ledger in assets:
            sub = AccountLedger.objects.filter(account_chart__group=ledger, total_value__gt=0)
            if sub:
                asset_dict['groups'].append({
                    "title":ledger.group,
                    "ledgers": []

                })
                for s in sub:
                    subledger = model_to_dict(s)
                    del subledger['id']
                    del subledger['account_chart']
                    del subledger['is_editable']
                    asset_dict['groups'][-1]["ledgers"].append(subledger)

        liabilities = AccountChart.objects.filter(Q(account_type="Liability") | Q(account_type="Equity") )
        for ledger in liabilities:
            sub = AccountLedger.objects.filter(account_chart__group=ledger, total_value__gt=0)
            if sub:
                liability_dict['groups'].append({
                    "title":ledger.group,
                    "ledgers": []

                })
                for s in sub:
                    subledger = model_to_dict(s)
                    del subledger['id']
                    del subledger['account_chart']
                    del subledger['is_editable']
                    liability_dict['groups'][-1]["ledgers"].append(subledger)

        asset_total = AccountLedger.objects.filter(account_chart__account_type='Asset').aggregate(Sum('total_value')).get('total_value__sum')
        liability_total = AccountLedger.objects.filter(Q(account_chart__account_type="Liability") | Q(account_chart__account_type="Equity") )\
                                    .aggregate(Sum('total_value')).get('total_value__sum')
        

        if asset_total and liability_total:
            if asset_total > liability_total:
                context['retained_earnings'] =  asset_total-liability_total
                context['retained_loss'] = 0
                context['liability_total'] = liability_total + asset_total-liability_total
                context['asset_total'] = asset_total

            else:
                context['retained_loss'] =  liability_total-asset_total
                context['retained_earnings'] = 0
                context['asset_total'] = asset_total + liability_total-asset_total
                context['liability_total'] = liability_total
            

        context['assets'] = asset_dict
        context['liabilities'] =  liability_dict
        return Response(context)

class LedgersAPIView(APIView):
    def get(self, request):
        ledgers = AccountLedger.objects.all()

        serializer = AccountLedgerSerializer(ledgers, many=True)

        return Response(serializer.data, 200)

from api.serializers.accounting import AccountSubLedgerSerializer
class SubLedgersAPI(APIView):
    def post(self, request, *args, **kwargs):
        ledger_name = request.data['ledger']

        ledger = AccountLedger.objects.get(ledger_name=ledger_name)
        if Organization.objects.first().show_zero_ledgers:

            subledgers = AccountSubLedger.objects.filter(ledger=ledger)
        else:
            subledgers = AccountSubLedger.objects.filter(ledger=ledger, total_value__gt=0.0)

        serializer = AccountSubLedgerSerializer(subledgers, many=True)

        return Response(serializer.data, 200)
    
from api.serializers.accounting import AccountSubLedgerSerializer
class ExpenseSubLedgersAPI(APIView):
    def post(self, request, *args, **kwargs):
        ledger_id = request.data['ledger']

        ledger = AccountLedger.objects.get(id=ledger_id)
        if Organization.objects.first().show_zero_ledgers:

            subledgers = AccountSubLedger.objects.filter(ledger=ledger)
        else:
            subledgers = AccountSubLedger.objects.filter(ledger=ledger)

        serializer = AccountSubLedgerSerializer(subledgers, many=True)

        return Response(serializer.data, 200)
    
class SundryLedgersAPI(APIView):
    def post(self, request, *args, **kwargs):
        group_name = request.data['group']

        # ledger = AccountLedger.objects.get(account_chart__group=group_name)
        if Organization.objects.first().show_zero_ledgers:

            ledgers = AccountLedger.objects.filter(account_chart__group=group_name)
        else:
            ledgers = AccountLedger.objects.filter(account_chart__group=group_name, total_value__gt=0.0)

        serializer = AccountLedgerSerializer(ledgers, many=True)

        return Response(serializer.data, 200)

