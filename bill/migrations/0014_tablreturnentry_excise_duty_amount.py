# Generated by Django 4.0.6 on 2025-04-23 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0013_tblsalesentry_excise_duty_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='tablreturnentry',
            name='excise_duty_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
