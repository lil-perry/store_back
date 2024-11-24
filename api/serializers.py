from .models import Cart
from rest_framework import serializers

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['session_id', 'created_at']


