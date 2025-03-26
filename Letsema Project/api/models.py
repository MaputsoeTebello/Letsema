from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime
 
class Borrower(models.Model):
    name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Loan(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
        ('repaid', 'Repaid'),
    )
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    # Add any additional fields
  

# Modified fields for Loan model
    purpose = models.TextField(blank=True, null=True)  # Purpose of the loan
    application_date = models.DateTimeField(default=timezone.now)  # Use default instead of auto_now_add
    approval_date = models.DateTimeField(null=True, blank=True)
    disbursement_date = models.DateTimeField(null=True, blank=True)

    
    def __str__(self):
        return f"Loan for {self.borrower.name} - {self.amount}"
        
    # You might want to add methods for calculating repayment schedule
    def calculate_monthly_payment(self):
        # Simple calculation (principal + interest) / term_months
        principal = float(self.amount)
        rate = float(self.interest_rate) / 100 / 12  # Monthly interest rate
        term = int(self.term_months)
        
        # Monthly payment formula: P * (r(1+r)^n) / ((1+r)^n - 1)
        if rate > 0:
            monthly_payment = principal * (rate * (1 + rate) ** term) / ((1 + rate) ** term - 1)
        else:
            monthly_payment = principal / term
            
        return round(monthly_payment, 2)
        
        # Add these imports if not already present


# Add these new models
class CreditHistory(models.Model):
    borrower = models.OneToOneField(Borrower, on_delete=models.CASCADE, related_name='credit_history')
    score = models.IntegerField(
        validators=[MinValueValidator(300), MaxValueValidator(850)],
        help_text="Credit score (300-850)"
    )
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Credit History for {self.borrower.name} - Score: {self.score}"

class CreditTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('loan_payment', 'Loan Payment'),
        ('credit_card', 'Credit Card'),
        ('mortgage', 'Mortgage'),
        ('utility', 'Utility Payment'),
        ('other', 'Other'),
    )
    
    credit_history = models.ForeignKey(CreditHistory, on_delete=models.CASCADE, related_name='transactions')
    transaction_date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    is_paid = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.transaction_date} - {self.description} - {self.amount}"
    
    class Meta:
        ordering = ['-transaction_date']


# Add these new models
class RepaymentSchedule(models.Model):
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name='repayment_schedule')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Repayment Schedule for Loan #{self.loan.id}"
    
    def generate_installments(self):
        """Generate installments for the repayment schedule"""
        # Delete existing installments if any
        self.installments.all().delete()
        
        # Calculate number of installments
        start_date = self.start_date
        num_installments = self.loan.term_months
        
        # Generate installments
        for i in range(num_installments):
            due_date = start_date + datetime.timedelta(days=30 * (i + 1))
            Installment.objects.create(
                repayment_schedule=self,
                installment_number=i + 1,
                due_date=due_date,
                amount=self.monthly_payment,
                status='pending'
            )
        
        # Update end date
        self.end_date = start_date + datetime.timedelta(days=30 * num_installments)
        self.save()

class Installment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('partially_paid', 'Partially Paid'),
    )
    
    repayment_schedule = models.ForeignKey(RepaymentSchedule, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Installment #{self.installment_number} for Loan #{self.repayment_schedule.loan.id}"
    
    class Meta:
        ordering = ['installment_number']

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('check', 'Check'),
        ('other', 'Other'),
    )
    
    installment = models.ForeignKey(Installment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment of {self.amount} for Installment #{self.installment.installment_number}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update installment status
        installment = self.installment
        total_paid = sum(payment.amount for payment in installment.payments.all())
        
        if total_paid >= installment.amount:
            installment.status = 'paid'
        elif total_paid > 0:
            installment.status = 'partially_paid'
        installment.save()
        
        
