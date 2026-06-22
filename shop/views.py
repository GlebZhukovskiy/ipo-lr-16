import openpyxl
from io import BytesIO
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.core.mail import EmailMessage
from .models import Product, Category, Manufacturer, Cart, CartItem

# ... (предыдущие функции product_list, product_detail, cart_view, add_to_cart, update_cart, remove_from_cart остаются без изменений) ...

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    manufacturer_id = request.GET.get('manufacturer')
    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id)
    return render(request, 'shop/product_list.html', {'products': products, 'categories': categories, 'manufacturers': manufacturers})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required(login_url='/admin/login/')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'shop/cart.html', {'cart': cart})

@login_required(login_url='/admin/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 1})
    if not item_created:
        if cart_item.quantity + 1 <= product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.error(request, f"Нельзя добавить больше, чем есть на складе ({product.stock} шт.)")
    return redirect('shop:cart_view')

@login_required(login_url='/admin/login/')
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            messages.error(request, f"Количество превышает доступный остаток на складе ({cart_item.product.stock} шт.)")
    return redirect('shop:cart_view')

@login_required(login_url='/admin/login/')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('shop:cart_view')


# === НОВЫЙ КОД ДЛЯ ЛАБЫ 19 ===

@login_required(login_url='/admin/login/')
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.error(request, "Ваша корзина пуста, оформление невозможно.")
        return redirect('shop:cart_view')

    if request.method == 'POST':
        address = request.POST.get('address', 'Не указан')
        
        # 1. Генерируем чек в формате Excel в память
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Чек заказа"
        
        # Заголовок чека
        ws.append(["Чек об оплате заказа"])
        ws.append([f"Покупатель: {request.user.username}"])
        ws.append([f"Адрес доставки: {address}"])
        ws.append([]) # пустая строка
        ws.append(["Товар", "Цена за шт.", "Количество", "Итоговая стоимость"])
        
        for item in cart_items:
            ws.append([item.product.name, item.product.price, item.quantity, item.item_cost])
            
            # Списываем количество со склада
            item.product.stock -= item.quantity
            item.product.save()

        ws.append([])
        ws.append(["Общая стоимость:", "", "", cart.total_cost])
        
        # Сохраняем в виртуальный файл (байт-поток)
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        
        # 2. Отправка чека по Email
        subject = f"Ваш чек из магазина настольных игр"
        body = f"Здравствуйте, {request.user.username}!\n\nБлагодарим за заказ. Ваш чек во вложении.\nАдрес доставки: {address}"
        user_email = request.user.email if request.user.email else "user@example.com"
        
        email = EmailMessage(subject, body, 'shop@boardgames.local', [user_email])
        # Прикрепляем сгенерированный Excel файл
        email.attach('receipt.xlsx', excel_file.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        email.send()
        
        # 3. Очищаем корзину
        cart_items.delete()
        
        return render(request, 'shop/checkout.html', {'success': True})

    return render(request, 'shop/checkout.html', {'cart': cart, 'success': False})

# === КОД ДЛЯ API (DRF) ===
from rest_framework import viewsets
from .serializers import CategorySerializer, ManufacturerSerializer, ProductSerializer, CartSerializer, CartItemSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer