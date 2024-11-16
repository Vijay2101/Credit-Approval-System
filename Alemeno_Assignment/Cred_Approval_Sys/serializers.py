from rest_framework import serializers
from .models import Customers_data

class CustomerSerializer(serializers.ModelSerializer):
    approved_limit = serializers.IntegerField()

    class Meta:
        model = Customers_data
        fields = '__all__'

