from .models import Cart, Category
from .models import Product
from .models import CartItem
from rest_framework import serializers



class CategotySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = CategotySerializer()
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price', 'stock_quantity']



class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_name', 'product_price', 'quantity']


    def validate(self, data):
        product = data.get('product')  
        quantity = data.get('quantity')

        if quantity > product.stock_quantity:
            raise serializers.ValidationError({
                'quantity': f"Only {product.stock_quantity} units of {product.name} are available."
            })

        return data
    
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['session_id', 'items']

