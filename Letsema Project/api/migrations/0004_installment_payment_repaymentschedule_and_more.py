# Generated by Django 5.1.7 on 2025-03-23 20:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_credithistory_credittransaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='Installment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('installment_number', models.PositiveIntegerField()),
                ('due_date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('overdue', 'Overdue'), ('partially_paid', 'Partially Paid')], default='pending', max_length=20)),
            ],
            options={
                'ordering': ['installment_number'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateField()),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('bank_transfer', 'Bank Transfer'), ('mobile_money', 'Mobile Money'), ('check', 'Check'), ('other', 'Other')], max_length=20)),
                ('reference_number', models.CharField(blank=True, max_length=50, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('installment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='api.installment')),
            ],
        ),
        migrations.CreateModel(
            name='RepaymentSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('monthly_payment', models.DecimalField(decimal_places=2, max_digits=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('loan', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='repayment_schedule', to='api.loan')),
            ],
        ),
        migrations.AddField(
            model_name='installment',
            name='repayment_schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='installments', to='api.repaymentschedule'),
        ),
    ]
