from django.db import models

# Create your models here.

class Customers_data(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=51)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField(unique=False)
    phone_number = models.CharField(max_length=15)
    monthly_salary = models.FloatField()
    approved_limit = models.FloatField()
    current_debt = models.FloatField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Loan_data(models.Model):
    customer = models.ForeignKey(Customers_data, on_delete=models.CASCADE)
    loan_id = models.IntegerField(unique=True)
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_repayment = models.FloatField()
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer}"