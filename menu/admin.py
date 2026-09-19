from django.contrib import admin
from .models import Category, MenuItem, RecipeItem


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_in_stock', 'is_vegetarian')
    list_filter = ('category', 'is_available', 'is_vegetarian')
    search_fields = ('name',)
    inlines = [RecipeItemInline]

    @admin.display(boolean=True)
    def is_in_stock(self, obj):
        return obj.is_in_stock
