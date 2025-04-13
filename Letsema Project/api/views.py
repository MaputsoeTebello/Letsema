from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Borrower, Loan , CreditHistory, CreditTransaction, RepaymentSchedule, Installment, Payment
from .serializers import BorrowerSerializer, LoanSerializer, CreditHistorySerializer, CreditTransactionSerializer, RepaymentScheduleSerializer, InstallmentSerializer, PaymentSerializer
import logging


logger = logging.getLogger(__name__)

@api_view(['GET'])
def api_root(request):
    return Response({
        "message": "Welcome to Letsema Loan Management API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "register": request.build_absolute_uri('register/'),
            "login": request.build_absolute_uri('login/'),
            "borrowers": request.build_absolute_uri('borrowers/'),
            "loans": request.build_absolute_uri('loans/'),
            "loan-application": request.build_absolute_uri('loan-application/'),
            "loan-decision": request.build_absolute_uri('loan-decision/1/'),  # Example with ID 1
            "token": request.build_absolute_uri('token/'),
             "credit-history": request.build_absolute_uri('credit-history/'),
            "borrower-credit-history": request.build_absolute_uri('credit-history/1/'),  # Example with borrower ID 1
            "credit-transactions": request.build_absolute_uri('credit-transactions/1/'),  # Example with credit history ID 1
             "repayment-schedules": request.build_absolute_uri('repayment-schedules/'),
            "loan-repayment-schedule": request.build_absolute_uri('repayment-schedules/1/'),  # Example with loan ID 1
            "installment-detail": request.build_absolute_uri('installments/1/'),  # Example with installment ID 1
            "payments": request.build_absolute_uri('payments/'),
            "installment-payments": request.build_absolute_uri('payments/1/'),  # Example with installment ID 1
            "overdue-installments": request.build_absolute_uri('overdue-installments/'),
            "borrower-repayments": request.build_absolute_uri('borrower-repayments/1/'),  # Example with borrower ID 1
        }
    })
    
class RegisterBorrowerView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to register

    def post(self, request):
        serializer = BorrowerSerializer(data=request.data)
        if serializer.is_valid():
            borrower = serializer.save()
            return Response({
                "message": "Borrower registered successfully!",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BorrowerViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Borrower.objects.all()
        name = self.request.query_params.get('name')

        if name:
            queryset = queryset.filter(name__icontains=name)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"error": "No borrowers found matching the criteria."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Loan.objects.all()
        status_param = self.request.query_params.get('status')
        borrower_id = self.request.query_params.get('borrower_id')

        if status_param:
            queryset = queryset.filter(status=status_param)

        if borrower_id:
            try:
                borrower_id = int(borrower_id)
                queryset = queryset.filter(borrower_id=borrower_id)
            except ValueError:
                # We can't return a Response from get_queryset, so we'll just return an empty queryset
                return Loan.objects.none()

        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"error": "No loans found matching the criteria."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        loan = get_object_or_404(Loan, pk=kwargs['pk'])
        serializer = self.get_serializer(loan)
        return Response(serializer.data)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        user_type = request.data.get('userType')
        email = request.data.get('email')
        
        if user_type == 'borrower':
            try:
                borrower = Borrower.objects.get(email=email)
                return Response({
                    "success": True,
                    "userType": "borrower",
                    "borrower": BorrowerSerializer(borrower).data
                })
            except Borrower.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Borrower not found"
                }, status=status.HTTP_404_NOT_FOUND)
        
        elif user_type == 'officer':
            # For simplicity, just return success for any loan officer login
            # In a real app, you would authenticate against actual loan officer accounts
            return Response({
                "success": True,
                "userType": "officer"
            })
        
        return Response({
            "success": False,
            "message": "Invalid user type"
        }, status=status.HTTP_400_BAD_REQUEST)

# New Loan Application Views
class LoanApplicationView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to submit a loan application
    
    def post(self, request):
        # Add validation for required fields
        if not request.data.get('borrower'):
            return Response({"error": "Borrower ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create loan application with pending status
        data = request.data.copy()
        data['status'] = 'pending'  # Set initial status to pending
        
        serializer = LoanSerializer(data=data)
        if serializer.is_valid():
            loan = serializer.save()
            
            # Log the loan application
            logger.info(f"New loan application submitted by borrower {loan.borrower.name} for amount {loan.amount}")
            
            return Response({
                "message": "Loan application submitted successfully!",
                "data": LoanSerializer(loan).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        # Get loan applications for a specific borrower
        borrower_id = request.query_params.get('borrower_id')
        if not borrower_id:
            return Response({"error": "Borrower ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            loans = Loan.objects.filter(borrower_id=borrower_id)
            serializer = LoanSerializer(loans, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving loan applications: {str(e)}")
            return Response({"error": "Failed to retrieve loan applications"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoanDecisionView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users (loan officers) can approve/reject
    
    def post(self, request, loan_id):
        try:
            loan = Loan.objects.get(pk=loan_id)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate the decision
        decision = request.data.get('decision')
        if decision not in ['approved', 'rejected']:
            return Response({"error": "Decision must be 'approved' or 'rejected'"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Update loan status
        loan.status = decision
        
        # If approved, set approval date
        if decision == 'approved':
            loan.approval_date = timezone.now()
            
            # Optional: You could add logic here to schedule disbursement
            # loan.disbursement_date = timezone.now() + timezone.timedelta(days=3)
        
        loan.save()
        
        # Log the decision
        logger.info(f"Loan application {loan_id} {decision} by user {request.user}")
        
        return Response({
            "message": f"Loan application {decision} successfully",
            "data": LoanSerializer(loan).data
        })
    
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(pk=loan_id)
            serializer = LoanSerializer(loan)
            return Response(serializer.data)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)
            
            
            # Add these imports if not already present


# Add these views to your existing views.py file
class CreditHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, borrower_id=None):
        """Get credit history for a specific borrower"""
        try:
            if borrower_id:
                # Get credit history for a specific borrower
                credit_history = get_object_or_404(CreditHistory, borrower_id=borrower_id)
                serializer = CreditHistorySerializer(credit_history)
                return Response(serializer.data)
            else:
                # Get credit history for the authenticated borrower
                # This assumes the user is linked to a borrower
                borrower = get_object_or_404(Borrower, email=request.user.email)
                credit_history = get_object_or_404(CreditHistory, borrower=borrower)
                serializer = CreditHistorySerializer(credit_history)
                return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving credit history: {str(e)}")
            return Response(
                {"error": "Failed to retrieve credit history"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create or update credit history"""
        # Only loan officers should be able to create/update credit history
        # In a real app, you would check if the user is a loan officer
        
        serializer = CreditHistorySerializer(data=request.data)
        if serializer.is_valid():
            # Check if credit history already exists for this borrower
            borrower_id = serializer.validated_data['borrower'].id
            credit_history, created = CreditHistory.objects.update_or_create(
                borrower_id=borrower_id,
                defaults=serializer.validated_data
            )
            
            response_serializer = CreditHistorySerializer(credit_history)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreditTransactionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, credit_history_id):
        """Get all transactions for a credit history"""
        try:
            transactions = CreditTransaction.objects.filter(credit_history_id=credit_history_id)
            serializer = CreditTransactionSerializer(transactions, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving credit transactions: {str(e)}")
            return Response(
                {"error": "Failed to retrieve credit transactions"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request, credit_history_id):
        """Add a new transaction to a credit history"""
        try:
            # Get the credit history
            credit_history = get_object_or_404(CreditHistory, id=credit_history_id)
            
            # Add credit_history to the data
            data = request.data.copy()
            data['credit_history'] = credit_history.id
            
            serializer = CreditTransactionSerializer(data=data)
            if serializer.is_valid():
                transaction = serializer.save()
                return Response(
                    CreditTransactionSerializer(transaction).data,
                    status=status.HTTP_201_CREATED
                )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error adding credit transaction: {str(e)}")
            return Response(
                {"error": "Failed to add credit transaction"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Add these views to your existing views.py file
class RepaymentScheduleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, loan_id=None):
        """Get repayment schedule for a loan"""
        try:
            if loan_id:
                # Get repayment schedule for a specific loan
                schedule = get_object_or_404(RepaymentSchedule, loan_id=loan_id)
                serializer = RepaymentScheduleSerializer(schedule)
                return Response(serializer.data)
            else:
                # Get all repayment schedules (admin/officer only)
                schedules = RepaymentSchedule.objects.all()
                serializer = RepaymentScheduleSerializer(schedules, many=True)
                return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving repayment schedule: {str(e)}")
            return Response(
                {"error": "Failed to retrieve repayment schedule"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request, loan_id):
        """Create a repayment schedule for a loan"""
        try:
            # Get the loan
            loan = get_object_or_404(Loan, id=loan_id)
            
            # Check if loan is approved
            if loan.status != 'approved':
                return Response(
                    {"error": "Cannot create repayment schedule for a loan that is not approved"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if repayment schedule already exists
            if hasattr(loan, 'repayment_schedule'):
                return Response(
                    {"error": "Repayment schedule already exists for this loan"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate total amount and monthly payment
            principal = float(loan.amount)
            rate = float(loan.interest_rate) / 100 / 12  # Monthly interest rate
            term = int(loan.term_months)
            
            # Calculate total amount (principal + interest)
            if rate > 0:
                monthly_payment = principal * (rate * (1 + rate) ** term) / ((1 + rate) ** term - 1)
                total_amount = monthly_payment * term
            else:
                monthly_payment = principal / term
                total_amount = principal
            
            # Create repayment schedule
            data = {
                'loan': loan.id,
                'total_amount': round(total_amount, 2),
                'monthly_payment': round(monthly_payment, 2),
                'start_date': request.data.get('start_date', timezone.now().date().isoformat()),
            }
            
            serializer = RepaymentScheduleSerializer(data=data)
            if serializer.is_valid():
                schedule = serializer.save()
                
                # Generate installments
                schedule.generate_installments()
                
                # Return updated schedule with installments
                response_serializer = RepaymentScheduleSerializer(schedule)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating repayment schedule: {str(e)}")
            return Response(
                {"error": f"Failed to create repayment schedule: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InstallmentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, installment_id):
        """Get details of a specific installment"""
        try:
            installment = get_object_or_404(Installment, id=installment_id)
            serializer = InstallmentSerializer(installment)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving installment: {str(e)}")
            return Response(
                {"error": "Failed to retrieve installment"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, installment_id):
        """Update installment status"""
        try:
            installment = get_object_or_404(Installment, id=installment_id)
            serializer = InstallmentSerializer(installment, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating installment: {str(e)}")
            return Response(
                {"error": "Failed to update installment"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, installment_id):
        """Record a payment for an installment"""
        try:
            # Get the installment
            installment = get_object_or_404(Installment, id=installment_id)
            
            # Add installment to the data
            data = request.data.copy()
            data['installment'] = installment.id
            
            # Set payment date to today if not provided
            if 'payment_date' not in data:
                data['payment_date'] = timezone.now().date().isoformat()
            
            serializer = PaymentSerializer(data=data)
            if serializer.is_valid():
                payment = serializer.save()
                
                # Return the payment with updated installment status
                response_serializer = PaymentSerializer(payment)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error recording payment: {str(e)}")
            return Response(
                {"error": f"Failed to record payment: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request, installment_id=None):
        """Get payments for an installment or all payments"""
        try:
            if installment_id:
                # Get payments for a specific installment
                payments = Payment.objects.filter(installment_id=installment_id)
            else:
                # Get all payments (admin/officer only)
                payments = Payment.objects.all()
            
            serializer = PaymentSerializer(payments, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving payments: {str(e)}")
            return Response(
                {"error": "Failed to retrieve payments"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OverdueInstallmentsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all overdue installments"""
        try:
            today = timezone.now().date()
            
            # Find installments that are due but not fully paid
            overdue_installments = Installment.objects.filter(
                due_date__lt=today,
                status__in=['pending', 'partially_paid']
            )
            
            serializer = InstallmentSerializer(overdue_installments, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving overdue installments: {str(e)}")
            return Response(
                {"error": "Failed to retrieve overdue installments"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BorrowerRepaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, borrower_id):
        """Get all repayment schedules for a borrower"""
        try:
            # Get all loans for the borrower
            loans = Loan.objects.filter(borrower_id=borrower_id)
            
            # Get repayment schedules for these loans
            schedules = RepaymentSchedule.objects.filter(loan__in=loans)
            
            serializer = RepaymentScheduleSerializer(schedules, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving borrower repayment schedules: {str(e)}")
            return Response(
                {"error": "Failed to retrieve borrower repayment schedules"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
