# Generated by Django 5.1.3 on 2024-11-16 14:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=122)),
            ],
        ),
        migrations.CreateModel(
            name='Customers_data',
            fields=[
                ('customer_id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=51)),
                ('last_name', models.CharField(max_length=50)),
                ('age', models.IntegerField()),
                ('phone_number', models.CharField(max_length=15)),
                ('monthly_salary', models.FloatField()),
                ('approved_limit', models.FloatField()),
                ('current_debt', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Loan_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_id', models.IntegerField(unique=True)),
                ('loan_amount', models.FloatField()),
                ('tenure', models.IntegerField()),
                ('interest_rate', models.FloatField()),
                ('monthly_repayment', models.FloatField()),
                ('emis_paid_on_time', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Cred_Approval_Sys.customers_data')),
            ],
        ),
    ]
