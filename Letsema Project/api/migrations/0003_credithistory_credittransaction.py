# Generated by Django 5.1.7 on 2025-03-23 19:32

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_loan_application_date_loan_approval_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(help_text='Credit score (300-850)', validators=[django.core.validators.MinValueValidator(300), django.core.validators.MaxValueValidator(850)])),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('borrower', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='credit_history', to='api.borrower')),
            ],
        ),
        migrations.CreateModel(
            name='CreditTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_date', models.DateField()),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_type', models.CharField(choices=[('loan_payment', 'Loan Payment'), ('credit_card', 'Credit Card'), ('mortgage', 'Mortgage'), ('utility', 'Utility Payment'), ('other', 'Other')], max_length=20)),
                ('is_paid', models.BooleanField(default=True)),
                ('credit_history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='api.credithistory')),
            ],
            options={
                'ordering': ['-transaction_date'],
            },
        ),
    ]
