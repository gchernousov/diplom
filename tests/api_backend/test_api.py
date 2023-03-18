import pytest
from rest_framework.test import APIClient, RequestsClient, force_authenticate, APIRequestFactory
from model_bakery import baker
import uuid


from api_backend.models import UserModel, Shop
from api_backend.views import ShopView
from rest_framework.authtoken.models import Token
from api_backend.serializers import UserSerializer
from api_backend.validation import check_login


URL = 'http://127.0.0.1:8000/api/v1'

TEST_PASSWORD = 't3St_pA4sw0Rd'


@pytest.fixture
def client():
    return APIClient()


# @pytest.fixture
# def test_password():
#     return 't3St_pA4sw0Rd'


@pytest.fixture
def create_buyer_user(db):
    def make_user(**kwargs):
        kwargs['password'] = TEST_PASSWORD
        kwargs['email'] = str(uuid.uuid4())[:8] + '@testmail.com'
        user = UserModel.objects.create(**kwargs)
        user.set_password(user.password)
        user.save()
        return user
    return make_user


@pytest.fixture
def create_shop_user(db):
    def make_user(**kwargs):
        kwargs['password'] = TEST_PASSWORD
        kwargs['email'] = str(uuid.uuid4())[:8] + '@testmail.com'
        kwargs['type'] = 'shop'
        user = UserModel.objects.create(**kwargs)
        user.set_password(user.password)
        user.save()
        return user
    return make_user



# def new_user(email, password, type):
#     user = UserModel(email=email, password=password, type=type)
#     user.set_password(password)
#     user.save()
#     return user


@pytest.fixture
def create_token(db, create_user):
    user = create_user()
    token, _ = Token.objects.get_or_create(user=user)
    print(f'-- create_token.token: {token}')
    return True


def new_token(user):
    token = Token.objects.get_or_create(user=user)
    return token


@pytest.mark.django_db
def test_account_register(client):
    print('>>> test_account_register')
    data = {'email': 'mrsmith@mail.com', 'password': 'Jn9c2Xy6Qm*1'}
    response = client.post(f'{URL}/user/register/', data=data, format='json')
    assert response.status_code == 200
    new_user = UserModel.objects.latest('pk')
    assert new_user.email == 'mrsmith@mail.com'


@pytest.mark.django_db
def test_account_login(client, create_buyer_user):
    print('>>> test_account_login')
    user = create_buyer_user()
    data = {'email': user.email, 'password': TEST_PASSWORD}
    response = client.post(f'{URL}/user/login/', data=data, format='json')
    assert response.status_code == 200
    response_data = response.json()
    result = 'Token' in response_data.keys()
    assert result is True


@pytest.mark.django_db
def test_create_shop(client, create_shop_user):
    print('>>> test_create_shop')
    user = create_shop_user()
    token, _ = Token.objects.get_or_create(user=user)
    token = str(token)
    new_shop = {'name': 'New Test Shop', 'url': 'http://testshop123.com/'}
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    request = client.post(f'{URL}/shop/', data=new_shop, format='json')
    # print(f'>>> request = {request}')
    # print(f'>>> request.json = {request.json()}')
    # assert 2 == 2
    assert request.status_code == 200
    shop = Shop.objects.latest('pk')
    assert shop.name == 'New Test Shop'


# @pytest.mark.django_db
# def test_get_products(client, create_token):
#     print('>>> test_get_products')
#     response = client.get(f'{URL}/products/')
#     print(f'>>> response.json: {response.json()}')
#     result = create_token()
#     # print(token)
#     # print(token.key)
#     assert 2 == 2
