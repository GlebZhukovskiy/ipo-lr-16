from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    country = models.CharField(max_length=100, verbose_name="Страна")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='products/', verbose_name="Фото товара")
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Цена")
    stock = models.IntegerField(verbose_name="Количество на складе")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

    def clean(self):
        if self.price is not None and self.price < 0:
            raise ValidationError({'price': 'Цена не может быть отрицательной.'})
        if self.stock is not None and self.stock < 0:
            raise ValidationError({'stock': 'Количество на складе не может быть отрицательным.'})

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

    @property
    def total_cost(self):
        return sum(item.item_cost for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Корзина")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"

    @property
    def item_cost(self):
        return self.product.price * self.quantity

    def clean(self):
        if self.product and self.quantity > self.product.stock:
            raise ValidationError({
                'quantity': f'Количество ({self.quantity}) превышает доступное на складе ({self.product.stock}).'
            })
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = [
        ('CUSTOMER', 'Покупатель'),
        ('ADMIN', 'Администратор'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CUSTOMER')
    full_name = models.CharField(max_length=255, blank=True, verbose_name="ФИО")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    address = models.TextField(blank=True, verbose_name="Адрес")
    
    # Индивидуальные поля:
    favorite_category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Любимый жанр игр")
    delivery_city = models.CharField(max_length=100, blank=True, verbose_name="Город доставки")

    def __str__(self):
        return f"Профиль: {self.user.username} ({self.get_role_display()})"

# Автоматическое создание профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Если создается суперпользователь, сразу делаем его ADMIN
        role = 'ADMIN' if instance.is_superuser else 'CUSTOMER'
        Profile.objects.create(user=instance, role=role)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()