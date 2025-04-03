# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import CartItemSerializer, CartSerializer, CategorySerializer, ProductSerializer, OrderSerializer, \
    ProductImageSerializer
import uuid

from .models import Cart, CartItem, Category, Product, ProductImage, Order
from django.db import transaction
from .serializers import CartSerializer
from rest_framework import mixins, viewsets

from .services.order_service import OrderService


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
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]


class ProductImageViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class CartView(APIView):
    def get_cart(self, request):
        session_id = request.session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id
        cart, created = Cart.objects.get_or_create(session_id=session_id)
        return cart

    def get(self, request):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)



# class CartItemView(APIView):
#     def post(self, request):
#         session_id = request.session.get('session_id')
#         serializer = CartItemSerializer(data=request.data, context={'session_id': session_id})
#         serializer.is_valid(raise_exception=True)
#         cart_item = serializer.save()

#         return Response({"item": CartItemSerializer(cart_item).data}, status=status.HTTP_201_CREATED)


#     def put(self, request, pk):
#         session_id = request.session.get('session_id')
#         cart_item = CartItemSerializer.get_cart_item(pk)
#         serializer = CartItemSerializer(cart_item, data=request.data, partial=False, context={'session_id': session_id})
#         serializer.is_valid(raise_exception=True)
#         updated_item = serializer.save()

#         return Response({"item": CartItemSerializer(updated_item).data}, status=status.HTTP_200_OK)



class CartItemViewSet(viewsets.ViewSet):
    def create(self, request):
        session_id = request.session.get('session_id')
        serializer = CartItemSerializer(data=request.data, context={'session_id': session_id})
        serializer.is_valid(raise_exception=True)
        cart_item = serializer.save()
        return Response({"item": CartItemSerializer(cart_item).data}, status=status.HTTP_201_CREATED)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        session_id = request.session.get('session_id')
        try:
            cart_item = CartItem.objects.get(pk=pk, cart__session_id=session_id)
        except CartItem.DoesNotExist:
            return Response({"message": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
        # cart_item = CartItemSerializer.get_cart_item(pk)
        serializer = CartItemSerializer(cart_item, data=request.data, partial=False, context={'session_id': session_id})
        serializer.is_valid(raise_exception=True)
        updated_item = serializer.save()
        return Response({"item": CartItemSerializer(updated_item).data}, status=status.HTTP_200_OK)


# hueta
# class OrderView(APIView):
#     def post(self, request):
#         session_id = request.session.get('session_id')
#         if not session_id:
#             return Response({"message": "No cart"}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             cart = Cart.objects.prefetch_related('items__product').get(session_id=session_id)
#         except Cart.DoesNotExist:
#             return Response({"message": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
#
#         print(cart.items.all())
#         if not cart.items.exists():
#             return Response({"message": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
#
#         serializer = OrderSerializer(data=request.data, context={'cart': cart})
#         serializer.is_valid(raise_exception=True)
#         order = serializer.save()




class OrderView(APIView):

    def post(self, request):
        session_id = request.session.get('session_id')

        if not session_id:
            return Response({"message": "no cart"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            return Response({"message": "no cart error"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = OrderService.create_order(
            email=serializer.validated_data["email"],
            phone_number=serializer.validated_data["phone_number"],
            delivery_address=serializer.validated_data["delivery_address"],
            cart=cart
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def get(self, request, pk):
        try:
            order = Order.objects.prefetch_related("items").get(id=pk)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

