from rest_framework.exceptions import APIException
from rest_framework.authtoken.models import Token
from django.db.models import ObjectDoesNotExist

from .models import UserModel, Shop


class APIError(APIException):
    status_code = 400
    default_detail = ''


def get_object(model, object_id):
    """Проверка наличия объекта в базе"""
    try:
        obj = model.objects.get(pk=object_id)
        return obj
    except ObjectDoesNotExist:
        return None


def check_login(email: str, password: str) -> bool:
    """Проверка соответствия email и password"""
    try:
        user = UserModel.objects.get(email=email)
    except ObjectDoesNotExist:
        return False
    if user.check_password(password):
        return True
    return False


def check_email(email: str) -> bool:
    """Проверка наличия email в базе"""
    try:
        UserModel.objects.get(email=email)
        return False
    except ObjectDoesNotExist:
        return True


def check_token(token):
    """Проверка наличия токена в базе"""
    try:
        token = Token.objects.get(key=token)
        return token
    except ObjectDoesNotExist:
        return None


def check_shop(user: object, shop_name: str) -> bool:
    """Проверка соответствия пользователя (менеджера магазина) и магазина"""
    try:
        shop = Shop.objects.get(owner=user)
        if shop.name == shop_name:
            return True
        return False
    except ObjectDoesNotExist:
        return True

def auth_check(request):
    """Проверка наличия токена в заголовке, его наличия в базе
    и возврат объекта пользователя, если все успешно"""

    if request.headers.get('Token') is None:
        raise APIError('Не указан Token. Вы не авторизованы.')
    token = check_token(request.headers['Token'])
    if token is None:
        raise APIError('Token неверный.')
    user = UserModel.objects.get(email=token.user)
    return user
