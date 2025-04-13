      
from rest_framework import serializers
from .models import Borrower, Loan , CreditTransaction , CreditHistory , Payment , Installment , RepaymentSchedule

class BorrowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrower
        fields = ['id', 'name', 'id_number', 'email', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']

class LoanSerializer(serializers.ModelSerializer):
    borrower_name = serializers.ReadOnlyField(source='borrower.name')
    monthly_payment = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = ['id', 'borrower', 'borrower_name', 'amount', 'interest_rate', 
                  'term_months', 'purpose', 'status', 'monthly_payment', 
                  'approval_date', 'disbursement_date', 'created_at']
        read_only_fields = ['id', 'approval_date', 'disbursement_date', 'created_at']
    
    def get_monthly_payment(self, obj):
        return obj.calculate_monthly_payment()
        
        
        # Add these serializers to your existing serializers.py file
class CreditTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = ['id', 'transaction_date', 'description', 'amount', 
                  'transaction_type', 'is_paid']
        read_only_fields = ['id']

class CreditHistorySerializer(serializers.ModelSerializer):
    transactions = CreditTransactionSerializer(many=True, read_only=True)
    borrower_name = serializers.ReadOnlyField(source='borrower.name')
    
    class Meta:
        model = CreditHistory
        fields = ['id', 'borrower', 'borrower_name', 'score', 'last_updated', 'transactions']
        read_only_fields = ['id', 'last_updated']
        
        # Add these serializers to your existing serializers.py file
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'installment', 'amount', 'payment_date', 'payment_method', 
                  'reference_number', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

class InstallmentSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    total_paid = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Installment
        fields = ['id', 'installment_number', 'due_date', 'amount', 'status', 
                  'payments', 'total_paid', 'remaining_amount']
        read_only_fields = ['id', 'installment_number', 'due_date', 'amount']
    
    def get_total_paid(self, obj):
        return sum(payment.amount for payment in obj.payments.all())
    
    def get_remaining_amount(self, obj):
        total_paid = self.get_total_paid(obj)
        return max(0, obj.amount - total_paid)

class RepaymentScheduleSerializer(serializers.ModelSerializer):
    installments = InstallmentSerializer(many=True, read_only=True)
    loan_details = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    remaining_balance = serializers.SerializerMethodField()
    
    class Meta:
        model = RepaymentSchedule
        fields = ['id', 'loan', 'loan_details', 'total_amount', 'monthly_payment', 
                  'start_date', 'end_date', 'installments', 'total_paid', 
                  'remaining_balance', 'created_at']
        read_only_fields = ['id', 'total_amount', 'monthly_payment', 'end_date', 'created_at']
    
    def get_loan_details(self, obj):
        return {
            'id': obj.loan.id,
            'borrower_name': obj.loan.borrower.name,
            'amount': obj.loan.amount,
            'term_months': obj.loan.term_months,
            'status': obj.loan.status
        }
    
    def get_total_paid(self, obj):
        return sum(
            payment.amount 
            for installment in obj.installments.all() 
            for payment in installment.payments.all()
        )
    
    def get_remaining_balance(self, obj):
        total_paid = self.get_total_paid(obj)
        return max(0, obj.total_amount - total_paid)
