from django.db import transaction
from rest_framework.exceptions import ValidationError
from api.models import Order, OrderItem, CartItem


class OrderService:
    @staticmethod
    def create_order(email, phone_number, delivery_address, cart):

        cart_items = CartItem.objects.filter(cart=cart).select_related("product")

        if not cart_items.exists():
            raise ValidationError("Cart is empty")

        for item in cart_items:
            if item.quantity > item.product.stock_quantity:
                raise ValidationError(
                    {"product": f"Недостаточно товара {item.product.name}. Доступно: {item.product.stock_quantity}"}
                )

        with transaction.atomic():
            order = Order.objects.create(
                email=email,
                phone_number=phone_number,
                delivery_address=delivery_address,
                total_price=0
            )

            total_price = 0
            order_items = []

            for item in cart_items:
                order_items.append(
                    OrderItem(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price_per_item=item.product.price
                    )
                )

                item.product.stock_quantity -= item.quantity
                item.product.save()

                total_price += item.product.price * item.quantity

            OrderItem.objects.bulk_create(order_items)


            order.total_price = total_price
            order.save()

            cart_items.delete()

        return order