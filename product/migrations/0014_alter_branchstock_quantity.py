# Generated by Django 4.0.6 on 2025-05-26 11:18

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_product_excise_duty_applicable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branchstock',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
        migrations.RunSQL(
            sql="UPDATE product_branchstock SET quantity = quantity * 1.00",
            reverse_sql="UPDATE product_branchstock SET quantity = ROUND(quantity)"
        ),
    ]
