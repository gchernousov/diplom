from rest_framework.exceptions import APIException
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


def check_shop(user: object, shop_name: str) -> bool:
    """Проверка соответствия пользователя (менеджера магазина) и магазина"""
    try:
        shop = Shop.objects.get(owner=user)
        if shop.name == shop_name:
            return True
        return False
    except ObjectDoesNotExist:
        return True
