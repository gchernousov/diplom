import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from api_backend.models import UserModel, Shop, Product, Category, Order, OrderItem

import random
import string


URL = 'http://127.0.0.1:8000/api/v1'

TEST_PASSWORD = 't3St_pA4sw0Rd'
TEST_SHOP = 'Test Shop'
TEST_FILE_URL = 'https://raw.githubusercontent.com/gchernousov/diplom/master/tests/api_backend/upload_test_shop_products.yml'


def generate_random_email():
    letters = string.ascii_lowercase
    email = ''.join(random.choice(letters) for i in range(12))
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
    shop = Shop.objects.create(name=TEST_SHOP, url='http://testshop123.com/', owner=user)
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
    new_shop = {'name': 'New Test Shop', 'url': 'http://testshop.xx/'}
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    response = client.post(f'{URL}/shop/', data=new_shop, format='json')
    assert response.status_code == 200
    shop = Shop.objects.latest('pk')
    assert shop.name == 'New Test Shop'
    assert shop.owner == user


@pytest.mark.django_db
def test_shop_update(client, create_shop):
    print('\n>>> test_shop_update')
    shop, token = create_shop
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    data = {'url': TEST_FILE_URL}
    response = client.post(f'{URL}/shop/update/', data=data, format='json')
    assert response.status_code == 200
    products = Product.objects.all()
    assert len(products) == 3
    product_1 = Product.objects.get(pk=1)
    assert product_1.name == 'Product 1'
    assert product_1.shop == shop


@pytest.mark.django_db
def test_update_basket(client, create_user):
    print('\n>>> test_update_basket')
    user_shop = create_user
    user_shop.type = 'shop'
    user_shop.save()
    shop = Shop.objects.create(name='New Test Shop', owner=user_shop)
    category = Category.objects.create(name='test_category_1')
    product = Product.objects.create(name='Test Product 1', shop=shop, category=category,
                                     external_id=1111, quantity=10, price=50000, price_rcc=59900)
    user_buyer = create_user
    token = Token.objects.create(user=user_buyer)
    token = str(token)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    data = {'items': [{'product': product.pk, 'quantity': 1}]}
    response = client.post(f'{URL}/basket/', data=data, format='json')
    assert response.status_code == 200
    result = response.json().get('Message')
    assert result == 'Товары добавлены в корзину'
    order = Order.objects.latest('pk')
    assert order.status == 'basket'
    order_items = OrderItem.objects.filter(order=order, product=product)
    assert order_items[0].product.name == 'Test Product 1'
