from django.shortcuts import render, HttpResponse
from .tasks import test_func, ingest_customer_data, ingest_loan_data

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customers_data, Loan_data
from .serializers import CustomerSerializer
import random
import math
import pandas as pd
from datetime import date
import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


# Create your views here.

def testing(request):
    return HttpResponse("Hello world")

# def celery_test(request):
#     test_func.delay()
#     return HttpResponse("Done")


# To injest provided data using background workers
def custormer_insert(request):
    ingest_customer_data.delay('customer_data.xlsx')
    return HttpResponse("Done")

# To injest provided data using background workers
def loan_insert(request):
    ingest_loan_data.delay('loan_data.xlsx')
    return HttpResponse("Done")



class RegisterCustomerAPIView(APIView):
    def post(self, request):
        data = request.data
        try:
            monthly_salary = data.get('monthly_salary')
            if not monthly_salary or not isinstance(monthly_salary, int):
                return Response({"error": "Invalid monthly income"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Approved credit limit calculation
            approved_limit = math.ceil((36 * monthly_salary) / 100000) * 100000
            
            # Generating a unique random customer ID
            while True:
                customer_id = random.randint(100000, 999999)  # Generate a random 6-digit ID
                if not Customers_data.objects.filter(customer_id=customer_id).exists():
                    break

            # Prepare customer data (phone_number as string for DB)
            customer_data = {
                'customer_id': customer_id,
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'age': data.get('age'),
                'monthly_salary': monthly_salary,
                'phone_number': str(data.get('phone_number')),  # Store as string in DB
                'approved_limit': approved_limit,
                'current_debt': 0
            }
            
            # Serialize and save customer data
            serializer = CustomerSerializer(data=customer_data)
            if serializer.is_valid():
                serializer.save()

                # Prepare the response data with required fields
                response_data = {
                    'customer_id': customer_id,
                    'name': f"{data.get('first_name')} {data.get('last_name')}",
                    'age': data.get('age'),
                    'monthly_salary': monthly_salary,
                    'approved_limit': approved_limit,
                    'phone_number': int(data.get('phone_number'))  # Return as integer in response
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class CheckEligibilityAPIView(APIView):
    def post(self, request):
        try:
            customer_id = request.data.get('customer_id')
            loan_amount = request.data.get('loan_amount')
            interest_rate = request.data.get('interest_rate')
            tenure = request.data.get('tenure')
         

            # Validating the required fields
            if not all([customer_id, loan_amount, interest_rate, tenure]):
                return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)
            
            loan_amount = float(loan_amount)
            interest_rate = float(interest_rate)
            tenure = int(tenure)
            customer_id = int(customer_id)

            print("2")
            # Retrieve the customer data from the database
            try:
                customer = Customers_data.objects.get(customer_id=customer_id)
            except Customers_data.DoesNotExist:
                return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
            print("3")
            # Calculate the credit score based on loan data
            try:
                loans = Loan_data.objects.filter(customer_id=customer_id)
            except Customers_data.DoesNotExist:
                return Response({"error": "Customer loan data not found"}, status=status.HTTP_404_NOT_FOUND)
           
            past_loans_paid_on_time = sum([loan.emis_paid_on_time for loan in loans])
            print(past_loans_paid_on_time)
            total_loans_taken = loans.count()
            loan_activity_current_year = loans.filter(start_date__year=date.today().year).count()
            loan_approved_volume = sum([loan.loan_amount for loan in loans])
            print("4")
            # Calculate the sum of all current loans
            current_loans = sum([loan.loan_amount for loan in loans])
            
            # If sum of current loans > approved limit, set credit score to 0
            if current_loans > customer.approved_limit:
                credit_score = 0
            else:
                credit_score = (
                    (past_loans_paid_on_time * 2) + 
                    (total_loans_taken * 1) + 
                    (loan_activity_current_year * 3) + 
                    (loan_approved_volume * 0.5)
                )

            # Adjust the credit score as needed
            credit_rating = min(credit_score, 100)  # Ensure credit rating doesn't exceed 100

            # Eligibility criteria based on credit rating
            approval = False
            corrected_interest_rate = interest_rate

            if credit_rating > 50:
                approval = True
            elif 50 >= credit_rating > 30:
                if interest_rate <= 12:
                    corrected_interest_rate = 16  
                approval = True
            elif 30 >= credit_rating > 10:
                if interest_rate <= 16:
                    corrected_interest_rate = 20 
                approval = True
            else:
                corrected_interest_rate = 25  # No loans approved if credit rating < 10

            # Check if the sum of all EMIs exceeds 50% of the monthly salary
            total_emis = sum([loan.monthly_repayment for loan in loans])
            if total_emis > (0.5 * customer.monthly_salary):
                approval = False

            # Calculate monthly installment
            print(loan_amount,type(loan_amount))
            monthly_installment = loan_amount / tenure
            print("6")
            # Prepare the response data
            response_data = {
                "customer_id": customer_id,
                "approval": approval,
                "interest_rate": interest_rate,
                "corrected_interest_rate": corrected_interest_rate,
                "tenure": tenure,
                "monthly_installment": monthly_installment
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class CreateLoan(APIView):
    def post(self, request):
        data = request.data
        customer_id = data.get("customer_id")
        loan_amount = data.get("loan_amount")
        interest_rate = data.get("interest_rate")
        tenure = data.get("tenure")

        # Check if customer exists
        try:
            customer = Customers_data.objects.get(customer_id=customer_id)
        except Customers_data.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

        # Call the eligibility API
        eligibility_response = requests.post("http://127.0.0.1:8000/check-eligibility/", json=data)
        eligibility_result = eligibility_response.json()

        if not eligibility_result.get("approval"):
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": eligibility_result.get("message"),
                "monthly_installment": None,
            }, status=status.HTTP_200_OK)

        # Generate a unique loan_id dynamically
        loan_id = random.randint(100000, 999999)

        # Calculate monthly installment
        monthly_installment = eligibility_result.get("monthly_installment")

        # Return loan approval response without storing in DB
        return Response({
            "loan_id": loan_id,
            "customer_id": customer_id,
            "loan_approved": True,
            "message": "Loan approved successfully",
            "monthly_installment": monthly_installment,
        }, status=status.HTTP_200_OK)
    

def view_loan_details(request, loan_id):
    """
    API to fetch loan details and customer details based on loan_id.
    """
    # Fetch the loan details
    loan = get_object_or_404(Loan_data, loan_id=loan_id)
    
    # Extract customer details
    customer = loan.customer

    # Build the response
    response_data = {
        "loan_id": loan.loan_id,
        "customer": {
            "id": customer.customer_id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone_number": customer.phone_number,
            "age": customer.age,
        },
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_repayment,
        "tenure": loan.tenure,
    }

    return JsonResponse(response_data, safe=False)



def view_loans_by_customer(request, customer_id):
    """
    API to fetch all current loan details for a given customer_id.
    """
    # Fetching the customer details
    customer = get_object_or_404(Customers_data, customer_id=customer_id)
    
    # Getting all loans for the customer
    loans = Loan_data.objects.filter(customer=customer)
    

    response_data = []
    for loan in loans:
        # Calculating remaining EMIs
        total_emis = loan.tenure
        emis_paid = loan.emis_paid_on_time
        repayments_left = max(total_emis - emis_paid, 0)  
        
        # Add loan details to the response list
        response_data.append({
            "loan_id": loan.loan_id,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_repayment,
            "repayments_left": repayments_left,
        })
    
    return JsonResponse(response_data, safe=False)