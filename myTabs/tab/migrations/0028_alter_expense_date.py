# Generated by Django 4.2.1 on 2023-06-19 14:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tab', '0027_alter_expense_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 19, 16, 51, 8, 938153)),
        ),
    ]