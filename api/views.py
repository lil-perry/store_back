# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CartItemSerializer, CartSerializer, CategotySerializer, ProductSerializer
import uuid

from .models import Cart, CartItem, Category, Product
from django.db import transaction
from .serializers import CartSerializer
from rest_framework import viewsets



# class CartCreateView(APIView):
#     def get(self, request):
#         session_id = request.session.session_key

#         if not session_id:
#             request.session.create()
#             session_id = request.session.session_key
        
#         cart, created = Cart.objects.get_or_create(session_id=session_id)
#         serializer = CartSerializer(cart)

#         return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategotySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



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



class CartItemView(APIView):
    def post(self, request):
        # Проверяем наличие session_id
        session_id = request.session.get('session_id')
        if not session_id:
            return Response({"message": "No cart"}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            return Response({"message": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        
        data = request.data.copy()
        data['cart'] = cart.id

        # новый элемент корзины
        serializer = CartItemSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        cart_item = serializer.save()

        return Response({"item": CartItemSerializer(cart_item).data}, status=status.HTTP_201_CREATED)


    def put(self, request, pk):
        # Находим элемент корзины по его ID
        try:
            cart_item = CartItem.objects.get(pk=pk)
        except CartItem.DoesNotExist:
            return Response({"message": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

        # Обновляем количество
        serializer = CartItemSerializer(cart_item, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated_item = serializer.save()

        return Response({"item": CartItemSerializer(updated_item).data}, status=status.HTTP_200_OK)



class OrderView(APIView):
    def post(self, request):
        session_id = request.session.get('session_id')
        if not session_id:
            return Response({"message": "No cart"}, status=status.HTTP_400_BAD_REQUEST)
                
        try:
            cart = Cart.objects.prefetch_related('items__product').get(session_id=session_id)
        except Cart.DoesNotExist:
            return Response({"message": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        
        print(cart.items.all())
        if not cart.items.exists():
            return Response({"message": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        