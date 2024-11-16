from celery import shared_task
import pandas as pd
from .models import Customers_data, Loan_data

@shared_task(bind=True)
def test_func(self):
    print("qwerty")
    for i in range(10):
        print(i)
    return "Done" 




@shared_task
def ingest_customer_data(file_path):
    data = pd.read_excel(file_path)
    for _, row in data.iterrows():
        print(row['Customer ID'],row['First Name'])
        Customers_data.objects.update_or_create(
            customer_id=row['Customer ID'],
            defaults={
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'age': row['Age'],
                'phone_number': row['Phone Number'],
                'monthly_salary': row['Monthly Salary'],
                'approved_limit': row['Approved Limit'],
                'current_debt': 0,
            }
        )

@shared_task
def ingest_loan_data(file_path):
    data = pd.read_excel(file_path)
    for _, row in data.iterrows():
        customer = Customers_data.objects.get(customer_id=row['Customer ID'])
        Loan_data.objects.update_or_create(
            loan_id=row['Loan ID'],
            defaults={
                'customer': customer,
                'loan_amount': row['Loan Amount'],
                'tenure': row['Tenure'],
                'interest_rate': row['Interest Rate'],
                'monthly_repayment': row['Monthly payment'],
                'emis_paid_on_time': row['EMIs paid on Time'],
                'start_date': row['Date of Approval'],
                'end_date': row['End Date'],
            }
        )
