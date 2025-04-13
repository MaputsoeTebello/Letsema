from django.contrib import admin
from .models import  Borrower, Loan, CreditHistory, CreditTransaction,RepaymentSchedule, Installment, Payment
   

@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ('name', 'id_number', 'email', 'phone', 'created_at')
    search_fields = ('name', 'id_number', 'email')
    list_filter = ('created_at',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('borrower', 'amount', 'interest_rate', 'term_months', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('borrower__name', 'borrower__id_number')
    

@admin.register(CreditHistory)
class CreditHistoryAdmin(admin.ModelAdmin):
    list_display = ('borrower', 'score', 'last_updated')
    search_fields = ('borrower__name', 'borrower__id_number')

@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ('credit_history', 'transaction_date', 'description', 'amount', 'transaction_type', 'is_paid')
    list_filter = ('transaction_type', 'is_paid', 'transaction_date')
    search_fields = ('description', 'credit_history__borrower__name')
    

class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 0

@admin.register(RepaymentSchedule)
class RepaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ('loan', 'total_amount', 'monthly_payment', 'start_date', 'end_date')
    search_fields = ('loan__borrower__name',)
    inlines = [InstallmentInline]

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ('repayment_schedule', 'installment_number', 'due_date', 'amount', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('repayment_schedule__loan__borrower__name',)
    inlines = [PaymentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('installment', 'amount', 'payment_date', 'payment_method', 'reference_number')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('installment__repayment_schedule__loan__borrower__name', 'reference_number')
