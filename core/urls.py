"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter

from menu.views import CategoryViewSet, MenuItemViewSet, RecipeItemViewSet
from tables.views import TableViewSet
from reservations.views import ReservationViewSet
from orders.views import OrderViewSet
from inventory.views import InventoryItemViewSet, StockMovementViewSet

from core.views import dashboard_view, UserRegisterView

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('menu-items', MenuItemViewSet, basename='menu-item')
router.register('recipe-items', RecipeItemViewSet, basename='recipe-item')
router.register('tables', TableViewSet, basename='table')
router.register('reservations', ReservationViewSet, basename='reservation')
router.register('orders', OrderViewSet, basename='order')
router.register('inventory', InventoryItemViewSet, basename='inventory')
router.register('stock-movements', StockMovementViewSet, basename='stock-movement')

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/register/', UserRegisterView.as_view(), name='register'),
    path('api/', include(router.urls)),
    path('api/', include('reports.urls')),
]

