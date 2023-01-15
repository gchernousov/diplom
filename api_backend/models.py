from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


USER_TYPES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
    ('admin', 'Администратор')
)

ORDER_STATUS = (
    ('basket', 'Корзина'),
    ('new', 'Новый'),
    ('confirmed', 'Обработан'),
    ('sent', 'На доставке'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен')
)


class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(email, password, **extra_fields)


class UserModel(AbstractUser):

    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=48, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=48, blank=True, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=48, blank=True, verbose_name='Отчество')
    company = models.CharField(max_length=48, blank=True, verbose_name='Компания')
    position = models.CharField(max_length=48, blank=True, verbose_name='Должность')
    type = models.CharField(max_length=5, choices=USER_TYPES, default='buyer', verbose_name='Тип пользователя')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Shop(models.Model):

    name = models.CharField(max_length=48, verbose_name='Название')
    url = models.URLField(null=True, blank=True, verbose_name='Ссылка')
    owner = models.OneToOneField(UserModel, verbose_name='Владелец магазина', on_delete=models.CASCADE)
    state = models.BooleanField(default=True, verbose_name='Статус получения заказов')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name


class Category(models.Model):

    name = models.CharField(max_length=48, verbose_name='Название')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(max_length=96, verbose_name='Название')
    category = models.ForeignKey(Category, related_name='products', blank=True,
                                 on_delete=models.CASCADE, verbose_name='Категория')
    shop = models.ForeignKey(Shop, related_name='products', on_delete=models.CASCADE, verbose_name='Магазин')
    external_id = models.PositiveIntegerField(verbose_name='Внешний ID')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rcc = models.PositiveIntegerField(verbose_name='Розничная цена')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Parameter(models.Model):

    name = models.CharField(max_length=48, verbose_name='Название')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'

    def __str__(self):
        return self.name


class ProductParameter(models.Model):

    product = models.ForeignKey(Product, related_name='product_parameters',
                                on_delete=models.CASCADE, verbose_name='Товар')
    parameter = models.ForeignKey(Parameter, related_name='product_parameters',
                                  on_delete=models.CASCADE, verbose_name='Параметр')
    value = models.CharField(max_length=48, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметр товара'
        verbose_name_plural = 'Параметры товаров'


class ClientContact(models.Model):

    user = models.ForeignKey(UserModel, related_name='contacts',
                             on_delete=models.CASCADE, verbose_name='Пользователь')
    city = models.CharField(max_length=48, verbose_name='Город')
    street = models.CharField(max_length=48, verbose_name='Улица')
    house = models.CharField(max_length=12, verbose_name='Номер дома')
    building = models.CharField(max_length=12, blank=True, verbose_name='Корпус/Строение')
    apartment = models.CharField(max_length=12, blank=True, verbose_name='Квартира')
    phone = models.CharField(max_length=24, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = 'Контакты пользователей'

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'


class Order(models.Model):

    user = models.ForeignKey(UserModel, related_name='orders',
                             on_delete=models.CASCADE, verbose_name='Пользователь')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=ORDER_STATUS, max_length=9, verbose_name='Статус заказа')
    contact = models.ForeignKey(ClientContact, on_delete=models.CASCADE,
                                blank=True, null=True, verbose_name='Контакт')


class OrderItem(models.Model):

    order = models.ForeignKey(Order, related_name='ordered_items',
                              on_delete=models.CASCADE, verbose_name='Номер заказа')
    product = models.ForeignKey(Product, related_name='ordered_items',
                                on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
