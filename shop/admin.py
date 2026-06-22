from django.contrib import admin
from .models import Category, Manufacturer, Product, Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'manufacturer')
    list_filter = ('category', 'manufacturer')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at', 'get_total_cost')
    inlines = [CartItemInline]

    def get_total_cost(self, obj):
        return obj.total_cost
    get_total_cost.short_description = "Общая стоимость"

admin.site.register(CartItem)
from django.contrib import admin
from .models import Profile

admin.site.register(Profile)