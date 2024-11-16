from django.urls import path
from . import views
from .views import RegisterCustomerAPIView,CheckEligibilityAPIView,CreateLoan,view_loan_details,view_loans_by_customer

urlpatterns = [
    path('',views.testing, name="testing" ),
    # path('celery_test/',views.celery_test, name="celery_test" ),
    path('custormer_insert/',views.custormer_insert, name="custormer_insert" ),
    path('loan_insert/',views.loan_insert, name="loan_insert" ),

    path('register/', RegisterCustomerAPIView.as_view(), name='register-customer'),
    path('check-eligibility/', CheckEligibilityAPIView.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoan.as_view(), name='create-loan'),
    path('view-loan/<int:loan_id>/', view_loan_details, name='view_loan_details'),
    path('view-loans/<int:customer_id>/', view_loans_by_customer, name='view_loans_by_customer'),
]
