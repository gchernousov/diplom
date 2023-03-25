from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

import requests
from yaml import load as load_yaml, Loader

from .validation import get_object, check_shop, check_login, check_email, auth_check, IsOwner
from .models import UserModel, Shop, ClientContact, Category, Product, \
    Parameter, ProductParameter, Order, OrderItem
from .serializers import UserSerializer, ContactSerializer, ShopSerializer, ShopDetailSerializer, \
    CategorySerializer, ProductSerializer, ProductDetailSerializer


# Вспомогательные функции

def order_price(product_list: list) -> int:
    """Подсчет общей суммы заказа"""
    price = 0
    for n in product_list:
        product = Product.objects.get(pk=n)
        price += product.price_rcc
    return price


def upd_quantity(order_id: int, product_id: int, quantity: int) -> int:
    """Сложение количества одинаковых товаров при повторном POST запросе в BasketView"""
    item = OrderItem.objects.filter(order_id=order_id, product_id=product_id)
    if len(item) == 0:
        return quantity
    quantity = item[0].quantity + quantity
    return quantity


# Views

class AccountRegister(APIView):

    """View для регистрации пользователей"""

    def post(self, request, *args, **kwargs):
        register_keys = {'email', 'password'}
        if register_keys.issubset(request.data):
            if check_email(request.data['email']):
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    new_user = user_serializer.save()
                    new_user.set_password(request.data['password'])
                    new_user.save()
                    return JsonResponse({'Status': 'OK', 'Message': 'Регистрация прошла успешно'})
                else:
                    return JsonResponse({'Status': 'Ошибка!', 'Error': user_serializer.errors})
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Пользователь с таким email уже существует'})
        return JsonResponse({'Status': 'Ошибка!', 'Error': 'Не указаны необходимые аргументы для регистрации'})


class AccountLogin(APIView):

    """View для получения Token"""

    def post(self, request, *args, **kwargs):
        register_keys = {'email', 'password'}
        if register_keys.issubset(request.data):
            if check_login(request.data['email'], request.data['password']):
                user = UserModel.objects.get(email=request.data['email'])
                token = Token.objects.get_or_create(user=user)
                return JsonResponse({'Status': 'OK', 'Token': str(token[0])})
            else:
                return JsonResponse({'Status': 'Ошибка!', 'Error': 'Неправильный email или пароль'})
        return JsonResponse({'Status': 'Ошибка!', 'Error': 'Необходим email и пароль'})


class ContactView(APIView):

    """View для работы с адресом доставки пользователя"""

    permission_classes = (IsAuthenticated, IsOwner,)

    def get_contact(self, user):
        try:
            contact = ClientContact.objects.get(user=user)
            return contact
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        contact = self.get_contact(request.user.id)
        if contact is None:
            return JsonResponse({'Status': ' Ошибка!', 'Error': 'Адрес отсутствует'})
        serializer = ContactSerializer(contact)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        contact_keys = {'city', 'street', 'house', 'phone'}
        if contact_keys.issubset(request.data):
            request.data['user'] = request.user.id
            serializer = ContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': 'Успешно!', 'Message': 'Адрес добавлен'})
            else:
                return JsonResponse({'Status': 'Ошибка!', 'Error': serializer.errors})
        return JsonResponse({'Status': 'Ошибка!', 'Error': 'Указаны не все параметры'})

    def patch(self, request, *args, **kwargs):
        contact = self.get_contact(request.user.id)
        if contact is None:
            return JsonResponse({'Status': ' Ошибка!', 'Error': 'Адрес отсутствует'})
        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'Status': 'Успешно!', 'Message': 'Адрес изменен'})
        else:
            return JsonResponse({'Status': 'Ошибка!', 'Error': serializer.errors})


class ShopView(APIView):

    """View для просмотра, добавления, изменения и удаления магазина"""

    permission_classes = (IsAuthenticated, IsOwner,)

    def get_shop(self, owner):
        try:
            shop = Shop.objects.get(owner=owner)
            return shop
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        shop = self.get_shop(request.user)
        if shop is not None:
            shop_serializer = ShopDetailSerializer(shop)
            return Response(shop_serializer.data)
        else:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'За вами нет закрепленного магазина'})

    def post(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'У вас нет прав на данное действие'})
        if {'name'}.issubset(request.data):
            request.data['owner'] = request.user.id
            shop_serializer = ShopSerializer(data=request.data)
            if shop_serializer.is_valid():
                shop_serializer.save()
                return Response(shop_serializer.data)
            else:
                return JsonResponse({'Status': 'Ошибка!', 'Error': shop_serializer.errors})
        else:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Необходимо ввести имя магазина (name)'})

    def patch(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'У вас нет прав на данное действие'})
        shop = self.get_shop(request.user)
        if shop is None:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'За вами нет закрепленного магазина'})
        shop_serializer = ShopSerializer(shop, data=request.data, partial=True)
        if shop_serializer.is_valid():
            shop_serializer.save()
            return JsonResponse({'Status': 'Успешно', 'Message': 'Магазин изменен'})
        else:
            return JsonResponse({'Status': 'Ошибка!', 'Error': shop_serializer.errors})

    def delete(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'У вас нет прав на данное действие'})
        shop = self.get_shop(request.user)
        if shop is None:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'За вами нет закрепленного магазина'})
        shop.delete()
        return JsonResponse({'Status': 'Успешно', 'Message': 'Магазин удален'})


class CategoryView(ListAPIView):

    """View для просмотра категорий и товаров в каждой категории"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductView(ListAPIView):

    """View для поиска товаров по названию, категории и стоимости"""

    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(shop__state=True)
        name = self.request.query_params.get('name')
        category = self.request.query_params.get('category')
        price_gte = self.request.query_params.get('price_gte')
        price_lte = self.request.query_params.get('price_lte')
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        if category is not None:
            queryset = queryset.filter(category=category)
        if price_gte is not None:
            queryset = queryset.filter(price_rcc__gte=price_gte)
        if price_lte is not None:
            queryset = queryset.filter(price_rcc__lte=price_lte)
        return queryset


class ProductDetailView(APIView):

    """View для полной информации о конкретном товаре"""

    def get(self, request, product_id, *args, **kwargs):
        product = get_object(Product, product_id)
        if product is not None:
            product_serializer = ProductDetailSerializer(product)
            return Response(product_serializer.data)
        else:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Товар не найден'})


class ShopUpdate(APIView):

    """View для добавления товаров в магазин по url из yaml-файла"""

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'У вас нет прав на данное действие'})

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError:
                return JsonResponse({'Status': 'Ошибка!', 'Error': 'Неверно указан URL'})
            file = requests.get(url).content
            data = load_yaml(file, Loader=Loader)

            shop_name = data.get('shop')
            if shop_name is None:
                return JsonResponse({'Status': 'Ошибка!', 'Error': 'Отсутствует название магазина'})
            if check_shop(request.user, shop_name) is False:
                return JsonResponse({'Status': 'Ошибка!', 'Error': 'Неправильное название магазина'})
            shop, _ = Shop.objects.get_or_create(name=shop_name, owner=request.user)

            products = data.get('goods')
            if products is None:
                return JsonResponse({'Status': 'Ошибка!', 'Error': 'Отсутствует список товаров'})
            for product in products:
                category, _ = Category.objects.get_or_create(name=product.get('category'))
                new_product, _ = Product.objects.update_or_create(
                    shop=shop, external_id=product['external_id'],
                    defaults={
                        'name': product.get('name'),
                        'brand': product.get('brand'),
                        'model': product.get('model'),
                        'category': category,
                        'quantity': product.get('quantity'),
                        'price': product.get('price'),
                        'price_rcc': product.get('price_rcc')
                    }
                )

                params = product.get('parameters')
                if params is not None:
                    for pname, pvalue in params.items():
                        param, _ = Parameter.objects.get_or_create(name=pname)

                        ProductParameter.objects.update_or_create(product=new_product, parameter=param,
                                                                  defaults={'value': pvalue})

            return JsonResponse({'Status': 'OK', 'Message': 'Товары успешно добавлены!'})
        return JsonResponse({'Status': 'Ошибка!', 'Error': 'Не указан URL'})


class ShopOrders(APIView):

    """View для просмотра всех заказов текущего магазина"""

    def get(self, request, *args, **kwargs):
        user = auth_check(request)
        if user.type != 'shop':
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'У вас нет прав на данное действие'})
        status = request.query_params.get('status')
        if status is not None:
            orders = Order.objects.filter(
                ordered_items__product__shop__owner=user, status=status).exclude(
                status='basket').select_related('user')
        else:
            orders = Order.objects.filter(
                ordered_items__product__shop__owner=user).exclude(
                status='basket').select_related('user')

        order_list = []
        order_ids = []
        for order in orders:
            if order.id not in order_ids:
                order_ids.append(order.id)
                order_list.append(order)

        result = []
        for order in order_list:
            products = order.ordered_items.filter(product__shop__owner=user)
            product_list = []
            for product in products:

                product_list.append(
                    {'external_id': product.product.external_id,
                     'name': product.product.name,
                     'quantity': product.quantity}
                )

            result.append(
                {'order': order.id,
                 'user': order.user.email,
                 'contact': {
                     'city': order.contact.city,
                     'street': order.contact.street,
                     'house': order.contact.house,
                     'phone': order.contact.phone
                 },
                 'date': str(order.date),
                 'status': order.status,
                 'product': product_list}
            )

        return JsonResponse({'Заказы': result})


class BasketView(APIView):

    """View для взаимодействия с корзиной"""

    permission_classes = (IsAuthenticated,)

    def get_basket(self, user):
        try:
            basket = Order.objects.get(user=user, status='basket')
            return basket
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        basket = self.get_basket(request.user)
        if basket is None:
            return JsonResponse({'Status': 'OK', 'Message': 'Корзина пуста'})
        items = OrderItem.objects.filter(order=basket.id)
        if len(items) == 0:
            return JsonResponse({'Status': 'OK', 'Message': 'Корзина пуста'})
        basket_items = []
        total_price = 0
        for item in items:
            total_price += item.product.price_rcc * item.quantity
            basket_items.append(
                {'ID': item.product.id, 'Товар': item.product.name,
                 'Цена': item.product.price_rcc, 'Кол-во': item.quantity}
            )
        return JsonResponse({'Status': 'OK', 'Корзина': basket_items, 'Примерная сумма заказа': total_price})

    def post(self, request, *args, **kwargs):
        items = request.data.get('items')
        if items is None:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Неправильно указан либо отсутствует параметр items'})
        order, _ = Order.objects.get_or_create(user=request.user, status='basket')
        for item in items:
            OrderItem.objects.update_or_create(order=order,
                                               product_id=item['product'],
                                               defaults={'quantity': upd_quantity(
                                                   order.id,
                                                   item['product'],
                                                   item['quantity'])})
        return JsonResponse({'Status': 'OK',
                             'Message': 'Товары добавлены в корзину'})

    def delete(self, request, *args, **kwargs):
        basket = self.get_basket(request.user)
        if basket is not None:
            delete_products = request.data.get('products').split(',')
            delete_products = [int(i) for i in delete_products]
            order_products = OrderItem.objects.filter(order=basket)
            if len(order_products) == 0:
                return JsonResponse({'Status': 'OK', 'Message': 'Корзина пуста'})
            for order_product in order_products:
                if order_product.product.id in delete_products:
                    order_product.delete()
            return JsonResponse({'Status': 'OK', 'Message': 'Товары удалены'})
        return JsonResponse({'Status': 'OK', 'Message': 'Корзина пуста'})


class OrderView(APIView):

    """View для оформления заказа"""

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(user=request.user).exclude(status='basket')
        if len(orders) == 0:
            return JsonResponse({'Status': 'Успешно', 'Заказы': 'У вас еще нет заказов'})
        order_list = []
        for order in orders:
            order_list.append(
                {'Заказ ID': order.id, 'Дата': order.date, 'Статус': order.status}
            )
        return JsonResponse({'Status': 'Успешно', 'Заказы': order_list})

    def post(self, request, *args, **kwargs):
        order = Order.objects.filter(user=request.user, status='basket')
        if len(order) == 0:
            return JsonResponse({'Status': 'Ошибка!',
                                 'Error': 'Прежде чем подтвердить заказ, добавьте товары в корзину'})
        try:
            contact = ClientContact.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Для оформления заказа необходимо заполнить адрес'})
        order.update(status='new', date=timezone.now(), contact=contact)
        return JsonResponse({'Status': 'Успешно', 'Message': 'Заказ оформлен'})
