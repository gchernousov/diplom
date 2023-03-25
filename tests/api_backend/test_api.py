import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from api_backend.models import UserModel, Shop, Product

import random
import string
import os


URL = 'http://127.0.0.1:8000/api/v1'

TEST_PASSWORD = 't3St_pA4sw0Rd'
TEST_SHOP = 'Test Shop'


def generate_random_email():
    letters = string.ascii_lowercase
    email = ''.join(random.choice(letters) for i in range (12))
    email = email + '@testmail.com'
    return email


# fixtures:

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def create_user(db):
    email = generate_random_email()
    user = UserModel.objects.create_user(email=email, password=TEST_PASSWORD)
    return user


@pytest.fixture
def create_token(db, create_user):
    user = create_user
    token, _ = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture
def create_shop(db, create_user):
    user = create_user
    user.type = 'shop'
    user.save()
    token = Token.objects.create(user=user)
    shop = Shop.objects.create(name='New Test Shop', url='http://testshop123.com/', owner=user)
    return shop, token


# tests:

@pytest.mark.django_db
def test_account_register(client):
    print('\n>>> test_account_register')
    data = {'email': 'mrsmith@mail.com', 'password': 'Jn9c2Xy6Qm*1'}
    response = client.post(f'{URL}/user/register/', data=data, format='json')
    assert response.status_code == 200
    new_user = UserModel.objects.latest('pk')
    assert new_user.email == 'mrsmith@mail.com'


@pytest.mark.django_db
def test_account_login(client, create_user):
    print('\n>>> test_account_login')
    user = create_user
    data = {'email': user.email, 'password': TEST_PASSWORD}
    response = client.post(f'{URL}/user/login/', data=data, format='json')
    assert response.status_code == 200
    response_data = response.json()
    result = 'Token' in response_data.keys()
    assert result is True


@pytest.mark.django_db
def test_create_shop(client, create_user):
    print('\n>>> test_create_shop')
    user = create_user
    user.type = 'shop'
    user.save()
    token = Token.objects.create(user=user)
    token = str(token)
    new_shop = {'name': TEST_SHOP, 'url': 'http://testshop.xx/'}
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    response = client.post(f'{URL}/shop/', data=new_shop, format='json')
    assert response.status_code == 200
    shop = Shop.objects.latest('pk')
    assert shop.name == 'New Test Shop'
    assert shop.owner == user


# @pytest.mark.django_db
# def test_shop_update(client, create_shop):
#     print('\n>>> test_shop_update')
#     shop, token = create_shop
#     client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
#     test_file = os.path.join('upload_shop_videomarket.yml')
#     print(test_file)
#     data = {'url': test_file}
#     response = client.post(f'{URL}/shop/update/', data=data, format='json')
#     print(f'> response.json(): {response.json()}')
#     # assert response.status_code == 200
#     # products = Product.objects.all()
#     # assert len(products) == 4
#     # product_1 = Product.objects.get(pk=1)
#     # assert product_1.name == 'Samsung Galaxy A13 4/64GB (черный)'
#     # assert product_1.shop == shop
#     assert 2 == 2