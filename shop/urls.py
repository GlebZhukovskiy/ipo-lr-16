from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Создаем роутер для DRF
router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'manufacturers', views.ManufacturerViewSet)
router.register(r'carts', views.CartViewSet)
router.register(r'cart-items', views.CartItemViewSet)

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.product_list, name='catalog'), # Твоя старая функция product_list теперь будет каталогом
    # Твои старые маршруты для обычных страниц (примерные, оставь свои как есть):
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # НОВЫЙ МАРШРУТ: Подключаем API роутер
    path('api/', include(router.urls)),
]