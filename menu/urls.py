from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MenuItemViewSet, RecipeItemViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('menu-items', MenuItemViewSet, basename='menu-item')
router.register('recipe-items', RecipeItemViewSet, basename='recipe-item')

urlpatterns = router.urls
