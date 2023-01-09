from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist

from .models import UserModel
from .serializers import UserSerializer


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
