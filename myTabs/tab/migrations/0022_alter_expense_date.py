# Generated by Django 4.2.1 on 2023-06-14 23:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tab', '0021_alter_expense_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 15, 1, 24, 0, 426626)),
        ),
    ]
