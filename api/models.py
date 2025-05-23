from django.db import models
import uuid
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


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

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="product_images/")
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



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
        return sum(item.quantity for item in self.items.all())

    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cart} x {self.product} {self.quantity}"



class Order(models.Model):
    access_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    delivery_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'pending'),
            ('processing', 'processing'),
            ('shipped', 'shipped'),
            ('delivered', 'delivered'),
            ('cancelled', 'cancelled'),
        ],
        default='pending',
    )


    def __str__(self):
        return f"Order {self.id} - {self.email} - {self.delivery_address}"

    def update_order_status(self, new_status: str):
        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered'],
            'delivered': [],
            'cancelled': []
        }

        if new_status not in valid_transitions[self.status]:
            raise ValidationError(f"Cannot change status from {self.status} to {new_status}")

        self.status = new_status
        self.save()
        return self





    # def calculate_total_price(self):
    #     self.total_price = sum(item.total_price() for item in self.items.all())
    #     self.save()

    # def save(self, *args, **kwargs):
    #     self.calculate_total_price()
    #     super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)

    def str(self):
        return f"{self.quantity} x {self.product.name}"

    def total_price(self):
        return self.quantity * self.product.price

    def save(self, *args, **kwargs):
        if not self.price_per_item:
            self.price_per_item = self.product.price
        super().save(*args, **kwargs)