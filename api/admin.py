from django.contrib import admin

# Register your models here.
from .models import Cart, CartItem, Product, Category, OrderItem, Order

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(OrderItem)
admin.site.register(Order)