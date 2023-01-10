from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist

from .models import UserModel, Shop
from .serializers import UserSerializer, ShopSerializer


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


def check(request):
    return JsonResponse({'Status': 'OK', 'View': 'check'})


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
