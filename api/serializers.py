from django.db import transaction

from .models import Cart, Category, OrderItem, Order, ProductImage
from .models import Product
from .models import CartItem
from rest_framework import serializers



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']

# class ProductSerializer(serializers.ModelSerializer):
#     images = ProductImageSerializer(many=True, read_only=True)
#     class Meta:
#         model = Product
#         fields = ['id', 'name', 'category', 'price', 'stock_quantity', 'images']
#         depth = 1

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price', 'stock_quantity', 'images']

    def create(self, validated_data):

        images_data = self.context['request'].FILES.getlist('images')  # Получаем список файлов
        product = Product.objects.create(**validated_data)  # Создаем товар

        for image in images_data:
            ProductImage.objects.create(product=product, image=image)

        return product

    def update(self, instance, validated_data):
        images_data = self.context['request'].FILES.getlist('images')

        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.price = validated_data.get('price', instance.price)
        instance.stock_quantity = validated_data.get('stock_quantity', instance.stock_quantity)
        instance.save()

        for image in images_data:
            ProductImage.objects.create(product=instance, image=image)

        return instance




class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True) 
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    cart = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all(), write_only=True, required=False)
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_name', 'product_price', 'quantity']


    def validate(self, data):

        session_id = self.context.get('session_id')

        if not session_id:
            raise serializers.ValidationError({"message": "No cart"})

        try:
            cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            raise serializers.ValidationError({"cart": "Cart not found."})

        data['cart'] = cart


        product = data.get('product')  
        quantity = data.get('quantity')

        if quantity > product.stock_quantity:
            raise serializers.ValidationError({
                'quantity': f"Only {product.stock_quantity} units of {product.name} are available."
            })

        return data
    
    # def get_cart_item(pk):
    #
    #     try:
    #         cart_item = CartItem.objects.get(pk=pk)
    #     except CartItem.DoesNotExist:
    #         raise serializers.ValidationError({"message": "Cart item not found"})
    #     return cart_item



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['session_id', 'items']



class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price_per_item', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    order_tracking_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'access_token', 'order_tracking_url', 'email', 'phone_number', 'delivery_address', 'status', 'total_price', 'items']


    def get_order_tracking_url(self, obj):
        return f"https://store.com/orders/track/{obj.access_token}/"


# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Order
#         fields = ['id', 'email', 'phone_number', 'delivery_address', 'status', 'items']
#
#
#     def validate(self, data):
#
#         session_id = self.context.get('session_id')
#
#         if not session_id:
#             raise serializers.ValidationError({"message": "No cart"})
#
#         try:
#             cart = Cart.objects.get(session_id=session_id)
#         except Cart.DoesNotExist:
#             raise serializers.ValidationError({"cart": "Cart not found."})
#
#         data['cart'] = cart
#         return data
#
#
#     def create(self, validated_data):
#         cart = validated_data.pop('cart')
#         cart_items = CartItem.objects.filter(cart=cart)
#
#         if not cart_items.exists():
#             raise serializers.ValidationError({"cart": "Cart is empty."})
#
#         for item in cart_items:
#             if item.quantity > item.product.stock_quantity:
#                 raise serializers.ValidationError({"product": f"Not enough stock for {item.product.name}. available: {item.product.stock_quantity}"})
#
#         with transaction.atomic():
#             order = Order.objects.create(**validated_data)
#             total_price = 0
#
#
#             for item in cart_items:
#                 OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price_per_item=item.product.price)
#                 item.product.stock_quantity -= item.quantity
#                 item.product.save()
#                 total_price += item.product.price * item.quantity
#
#             order.total_price = total_price
#             order.save()
#
#         return order



