"""
URL configuration for prjct project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from api.views import *


router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImageViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'cartitem', CartItemViewSet, basename='cartitem')
router.register(r'order', OrderViewSet, basename='order')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/cart/', CartView.as_view(), name='cart_create'),
    # path('api/order/', OrderView.as_view(), name='order'),
    # path('api/cartitem/', CartItemView.as_view(), name='cartitem'),
    # path('api/cartitem/<int:pk>/', CartItemView.as_view(), name='cartitem_update'),
    path('api/', include(router.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
