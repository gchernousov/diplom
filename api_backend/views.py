from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import requests
from yaml import load as load_yaml, Loader
from pprint import pprint

from .models import UserModel, Shop, Category, Product, Parameter, ProductParameter
from .serializers import UserSerializer, ShopSerializer, CategorySerializer, ProductSerializer


def validate_email(email):
    query = UserModel.objects.filter(email=email)
    if len(query) == 0:
        return True
    return False


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


class AccountRegister(APIView):

    def get(self, request, *args, **kwargs):
        queryset = UserModel.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        register_keys = {'email', 'password', 'first_name', 'last_name', 'company', 'position', 'type'}
        if register_keys.issubset(request.data):
            if validate_email(request.data['email']):
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
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


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

            # pprint(data)
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
                # new_product = Product.objects.create(
                #     name=product['name'],
                #     category=category,
                #     shop=shop,
                #     external_id=product['external_id'],
                #     quantity=product['quantity'],
                #     price=product['price'],
                #     price_rcc=product['price_rcc']
                # )
                for pname, pvalue in product['parameters'].items():
                    param, _ = Parameter.objects.get_or_create(name=pname)

                    ProductParameter.objects.update_or_create(product=new_product, parameter=param,
                                                              defaults={'value': pvalue})

            return JsonResponse({'Status': 'OK', 'Message': 'Товары успешно добавлены!'})

        return JsonResponse({'Status': 'Ошибка!', 'Error': 'Не указан URL'})
