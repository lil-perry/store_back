from django.db import models
import uuid
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def is_in_stock(self):
        return self.stock_quantity > 0



class Cart(models.Model):
    session_id = models.UUIDField(
        default=uuid.uuid4, 
        unique=True, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Cart (Session: {self.session_id})"

    def total_quantity(self):
        """Общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())

    def total_price(self):
        """Общая стоимость товаров в корзине"""
        return sum(item.product.price * item.quantity for item in self.items.all())



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_item_total_price(self):
        """Цена для данного элемента корзины"""
        return self.product.price * self.quantity




