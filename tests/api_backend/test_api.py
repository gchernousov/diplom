import pytest
from rest_framework.test import APIClient
from model_bakery import baker

from api_backend.models import UserModel
from api_backend.serializers import UserSerializer
from api_backend.validation import check_login


URL = 'http://127.0.0.1:8000/'


@pytest.fixture
def client():
    return APIClient()


# @pytest.fixture
# def add_user():
#     data = {'email': 'testuser@testmail.com', 'password': 'hT3x*2NSdP9bA'}
#     user_serializer = UserSerializer(data=data)
#     if user_serializer.is_valid():
#         user = user_serializer.save()
#         user.set_password(data['password'])
#         user.save()
#
#         return user
#     return False



def new_user(email, password):
    user = UserModel(email=email, password=password)
    user.set_password(password)
    user.save()
    return user


# @pytest.fixture
# def add_new_user():
#     def factory(*args, **kwargs):
#         return baker.make(UserModel, *args, **kwargs)
#     return factory


# def get_object(model, object_id):
#     object = model.objects.get(pk=object_id)
#     return object


@pytest.mark.django_db
def test_account_register(client):
    print('>>> test_account_register')
    data = {'email': 'mrsmith@mail.com', 'password': 'Jn9c2Xy6Qm*1'}
    response = client.post(f'{URL}api/v1/user/register/', data=data, format='json')
    assert response.status_code == 200
    new_user = UserModel.objects.latest('pk')
    print(f'new_user = {new_user}')
    assert new_user.email == 'mrsmith@mail.com'


@pytest.mark.django_db
def test_account_login(client):
    print('>>> test_account_login')
    data = {'email': 'testuser@yandex.ru', 'password': 'Xg5ca9Lw2*k'}
    user = new_user(data['email'], data['password'])
    print(f'user.email = {user.email}, user.password = {user.password}')
    response = client.post(f'{URL}api/v1/user/login/', data=data, format='json')
    assert response.status_code == 200
    response_data = response.json()
    print(f'response_data = {response_data}')
    result = 'Token' in response_data.keys()
    assert result == True
