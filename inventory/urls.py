from rest_framework.routers import DefaultRouter
from .views import InventoryItemViewSet, StockMovementViewSet

router = DefaultRouter()
router.register('inventory', InventoryItemViewSet, basename='inventory')
router.register('stock-movements', StockMovementViewSet, basename='stock-movement')

urlpatterns = router.urls
