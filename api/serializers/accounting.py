from rest_framework import serializers
from accounting.models import TblJournalEntry, TblDrJournalEntry, TblCrJournalEntry, AccountLedger

class DrJournalEntrySerialzier(serializers.ModelSerializer):
    ledger = serializers.StringRelatedField()
    sub_ledger = serializers.StringRelatedField()

    class Meta:
        model = TblDrJournalEntry
        exclude = 'created_at', "updated_at"


class CrJournalEntrySerialzier(serializers.ModelSerializer):
    ledger = serializers.StringRelatedField()
    sub_ledger = serializers.StringRelatedField()
    class Meta:
        model = TblCrJournalEntry
        exclude = 'created_at', "updated_at"


class JournalEntryModelSerializer(serializers.ModelSerializer):
    debit_entries = DrJournalEntrySerialzier(many=True, read_only=True, source="tbldrjournalentry_set")
    credit_entries = CrJournalEntrySerialzier(many=True, read_only=True, source="tblcrjournalentry_set")

    class Meta:
        model = TblJournalEntry
        exclude = "updated_at",

class AccountLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountLedger
        fields = "ledger_name", "total_value", "id"

from accounting.models import AccountSubLedger
class AccountSubLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountSubLedger
        fields = "sub_ledger_name", "total_value", "id"
