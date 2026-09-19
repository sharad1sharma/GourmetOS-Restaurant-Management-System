from rest_framework import serializers
from .models import Table


class TableSerializer(serializers.ModelSerializer):
    table_number = serializers.IntegerField(source='number', read_only=True)
    is_available_now = serializers.BooleanField(read_only=True)

    class Meta:
        model = Table
        fields = ['id', 'number', 'table_number', 'capacity', 'location', 'status', 'is_available_now']
