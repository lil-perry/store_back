# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart
from .serializers import CartSerializer
import uuid

# class CartCreateView(APIView):
#     def get(self, request):
#         session_id = request.session.session_key

#         if not session_id:
#             request.session.create()
#             session_id = request.session.session_key
        
#         cart, created = Cart.objects.get_or_create(session_id=session_id)
#         serializer = CartSerializer(cart)

#         return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem, Product
from .serializers import CartSerializer

class CartView(APIView):
    def get_cart(self, request):
        """Получение корзины по session_id или пользователю"""
        session_id = request.session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id
        cart, created = Cart.objects.get_or_create(session_id=session_id)
        return cart

    def get(self, request):
        """Получение данных о корзине"""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

# class AddToCartView(APIView):
#     def post(self, request):
#         """Добавление товара в корзину"""
#         cart = CartView().get_cart(request)
#         product_id = request.data.get('product_id')
#         quantity = int(request.data.get('quantity', 1))

#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

#         # Проверяем, есть ли такой товар в корзине
#         cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

#         if not created:
#             cart_item.quantity += quantity  # Увеличиваем количество
#         else:
#             cart_item.quantity = quantity

#         if cart_item.quantity > product.stock_quantity:
#             return Response({"error": "Not enough stock available"}, status=status.HTTP_400_BAD_REQUEST)

#         cart_item.save()
#         serializer = CartItemSerializer(cart_item)
#         return Response(serializer.data, status=status.HTTP_200_OK)