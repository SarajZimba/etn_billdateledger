# Generated by Django 4.0.6 on 2025-07-01 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0007_expense_credit_sub_ledger_expense_journal_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tbljournalentry',
            name='entry_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
