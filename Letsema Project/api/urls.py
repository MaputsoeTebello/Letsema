
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterBorrowerView, BorrowerViewSet, 
    LoanViewSet, LoginView, api_root,
    LoanApplicationView, LoanDecisionView,
    CreditHistoryView, CreditTransactionView,
    RepaymentScheduleView, InstallmentView, PaymentView,
    OverdueInstallmentsView, BorrowerRepaymentView,
)

router = DefaultRouter()
router.register(r'borrowers', BorrowerViewSet)
router.register(r'loans', LoanViewSet)

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
    path('register/', RegisterBorrowerView.as_view(), name='register_borrower'),
    path('login/', LoginView.as_view(), name='login'),
    path('loan-application/', LoanApplicationView.as_view(), name='loan_application'),
    path('loan-decision/<int:loan_id>/', LoanDecisionView.as_view(), name='loan_decision'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('credit-history/', CreditHistoryView.as_view(), name='credit_history'),
    path('credit-history/<int:borrower_id>/', CreditHistoryView.as_view(), name='borrower_credit_history'),
    path('credit-transactions/<int:credit_history_id>/', CreditTransactionView.as_view(), name='credit_transactions'),
    path('repayment-schedules/', RepaymentScheduleView.as_view(), name='repayment_schedules'),
    path('repayment-schedules/<int:loan_id>/', RepaymentScheduleView.as_view(), name='loan_repayment_schedule'),
    path('installments/<int:installment_id>/', InstallmentView.as_view(), name='installment_detail'),
    path('payments/', PaymentView.as_view(), name='payments'),
    path('payments/<int:installment_id>/', PaymentView.as_view(), name='installment_payments'),
    path('overdue-installments/', OverdueInstallmentsView.as_view(), name='overdue_installments'),
    path('borrower-repayments/<int:borrower_id>/', BorrowerRepaymentView.as_view(), name='borrower_repayments'),
]
