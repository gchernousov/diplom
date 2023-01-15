from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import requests
from yaml import load as load_yaml, Loader

from .models import UserModel, Shop, Category, Product, Parameter, ProductParameter, Order, OrderItem
from .serializers import UserSerializer, ShopSerializer, CategorySerializer, \
    ProductSerializer, ProductDetailSerializer, OrderItemSerializer


def validate_email(email):
    try:
        UserModel.objects.get(email=email)
        return False
    except ObjectDoesNotExist:
        return True


def check_login(email, password):
    try:
        user = UserModel.objects.get(email=email)
    except ObjectDoesNotExist:
        return False
    if user.check_password(password):
        return True
    return False


def check_token(token):
    try:
        token = Token.objects.get(key=token)
        return token
    except ObjectDoesNotExist:
        return None


def check_shop(user_id, shop_name):
    try:
        shop = Shop.objects.get(owner=user_id)
        if shop.name == shop_name:
            return True
        return False
    except ObjectDoesNotExist:
        return True


def order_price(product_list):
    price = 0
    for n in product_list:
        product = Product.objects.get(pk=n)
        price += product.price_rcc
    return price


class AccountRegister(APIView):

    def get(self, request, *args, **kwargs):
        queryset = UserModel.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        register_keys = {'email', 'password'}
        if register_keys.issubset(request.data):
            if validate_email(request.data['email']):
                # добавить проверку email и password (validate)
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


class ShopView(APIView):

    def get(self, request, *args, **kwargs):
        shops = Shop.objects.all()
        shop_serializer = ShopSerializer(shops, many=True)
        return Response(shop_serializer.data)

    def post(self, request, *args, **kwargs):
        if request.headers.get('Token') is None:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Вы не авторизованы'})
        token = check_token(request.headers['Token'])
        if token is not None:
            user = UserModel.objects.get(email=token.user)
            if user.type != 'shop':
                return JsonResponse({'Status': 'Ошибка!', 'Error': 'У вас нет прав на данное действие'})
            if {'name'}.issubset(request.data):
                request.data['owner'] = user.id
                shop_serializer = ShopSerializer(data=request.data)
                if shop_serializer.is_valid():
                    shop_serializer.save()
                    return Response(shop_serializer.data)
                else:
                    return JsonResponse({'Status': 'Ошибка!', 'Error': shop_serializer.errors})
            else:
                return JsonResponse({'Status': 'Ошибка!', 'Error': 'Необходимо ввести имя магазина (name)'})
        return JsonResponse({'Status': 'Ошибка!', 'Error': 'Token неверный'})


class ShopDetailView(APIView):

    def get_object(self, shop_id):
        try:
            shop = Shop.objects.get(pk=shop_id)
            return shop
        except ObjectDoesNotExist:
            return None

    def get(self, request, shop_id, *args, **kwargs):
        shop = self.get_object(shop_id)
        if shop is not None:
            shop_serializer = ShopSerializer(shop)
            return Response(shop_serializer.data)
        else:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Магазин не найден'})

    def patch(self, request, shop_id, *args, **kwargs):
        shop = self.get_object(shop_id)
        if shop is not None:
            if request.headers.get('Token') is None:
                return JsonResponse({'Status': 'Ошибка!', 'Error': 'Вы не авторизованы'})
            token = check_token(request.headers['Token'])
            if token is not None:
                user = UserModel.objects.get(email=token.user)
                if user.id == shop.owner_id:
                    shop_serializer = ShopSerializer(shop, data=request.data, partial=True)
                    if shop_serializer.is_valid():
                        shop_serializer.save()
                    return JsonResponse({'Status': 'OK', 'Message': 'Магазин изменен'})
                else:
                    return JsonResponse({'Status': 'Ошибка!', 'Error': 'У вас нет прав'})
            else:
                return JsonResponse({'Status': 'Ошибка!', 'Error': 'Token неверный'})
        else:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Магазин не найден'})

    def delete(self, request, shop_id, *args, **kwargs):
        shop = self.get_object(shop_id)
        if shop is not None:
            if request.headers.get('Token') is None:
                return JsonResponse({'Status': 'Ошибка!', 'Error': 'Вы не авторизованы'})
            token = check_token(request.headers['Token'])
            if token is not None:
                user = UserModel.objects.get(email=token.user)
                if user.id == shop.owner_id:
                    shop.delete()
                    return JsonResponse({'Status': 'OK', 'Message': 'Магазин удален'})
                else:
                    return JsonResponse({'Status': 'Ошибка!', 'Error': 'У вас нет прав'})
            else:
                return JsonResponse({'Status': 'Ошибка!', 'Error': 'Token неверный'})
        else:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Магазин не найден'})


class CategoryView(APIView):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class ProductView(APIView):

    def get(self, request, *args, **kwargs):
        search = request.query_params.get('name')
        if search is None:
            products = Product.objects.filter(shop__state=True)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        products = Product.objects.filter(shop__state=True, name__icontains=search)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailView(APIView):

    def get_object(self, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            return product
        except ObjectDoesNotExist:
            return None

    def get(self, request, product_id, *args, **kwargs):
        product = self.get_object(product_id)
        if product is not None:
            product_serializer = ProductDetailSerializer(product)
            return Response(product_serializer.data)
        else:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Товар не найден'})


class ShopUpdate(APIView):

    def post(self, request, *args, **kwargs):

        if request.headers.get('Token') is None:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Вы не авторизованы'})
        token = check_token(request.headers['Token'])
        if token is None:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Token неверный'})
        user = UserModel.objects.get(email=token.user)
        if user.type != 'shop':
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
            else:
                # if check_shop(user.id, shop_name):
                shop,_ = Shop.objects.get_or_create(name=shop_name, owner=user.id)

            products = data.get('goods')
            if products is None:
                return JsonResponse({'Status': 'Ошибка!', 'Error': 'Отсутствует список товаров'})
            for product in products:
                category, _ = Category.objects.get_or_create(name=product['category'])
                new_product, _ = Product.objects.update_or_create(
                    shop=shop, external_id=product['external_id'],
                    defaults={
                        'name': product['name'],
                        'category': category,
                        'quantity': product['quantity'],
                        'price': product['price'],
                        'price_rcc': product['price_rcc']
                    }
                )

                for pname, pvalue in product['parameters'].items():
                    param, _ = Parameter.objects.get_or_create(name=pname)

                    ProductParameter.objects.update_or_create(product=new_product, parameter=param,
                                                              defaults={'value': pvalue})

            return JsonResponse({'Status': 'OK', 'Message': 'Товары успешно добавлены!'})

        return JsonResponse({'Status': 'Ошибка!', 'Error': 'Не указан URL'})


class BasketView(APIView):

    def get_object(self, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            return product
        except ObjectDoesNotExist:
            return None

    def get(self):
        pass

    def post(self, request, *args, **kwargs):

        if request.headers.get('Token') is None:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Вы не авторизованы'})
        token = check_token(request.headers['Token'])
        if token is None:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Token неверный'})
        user = UserModel.objects.get(email=token.user)
        if user.type == 'shop':
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'У вас нет прав на данное действие'})

        items = request.data.get('items')
        if items is None:
            return JsonResponse({'Status': 'Ошибка!', 'Error': 'Неправильно указан либо отсутствует параметр items'})
        order = Order.objects.create(user=user, status='basket')
        product_list = []
        for item in items:
            product_list.append(item['product'])
            item['order'] = order.id
            serializer = OrderItemSerializer(data=item)
            if serializer.is_valid():
                serializer.save()

        price = order_price(product_list)
        return JsonResponse({'Status': 'Успешно',
                             'Message': 'Товары добавлены в корзину',
                             'Номер заказа': order.id,
                             'Общая сумма заказа': price})

    def patch(self):
        pass

    def delete(self):
        pass