import pytest
from rest_framework.test import APIClient

from api_backend.models import UserModel
from api_backend.serializers import UserSerializer


URL = 'http://127.0.0.1:8000/'


@pytest.fixture
def client():
    return APIClient()


# @pytest.fixture
# def add_user():
#     user = UserModel(email='testuser@testmail.com', password='pG6bc4Xo9Ms')
#     return user

# def get_object(model, object_id):
#     object = model.objects.get(pk=object_id)
#     return object

@pytest.mark.django_db
def test_account_register(client):
    data = {'email': 'mrsmith@mail.com', 'password': 'Jn9c2Xy6Qm*1'}
    response = client.post(f'{URL}api/v1/user/register/', data=data, format='json')
    assert response.status_code == 200
    new_user = UserModel.objects.latest('pk')
    assert new_user.email == 'mrsmith@mail.com'


@pytest.mark.django_db
def test_account_login(client):
    user = UserModel(email='testuser@testmail.com', password='pG6bc*4Xo9Ms')
    user.save()
    print(f'user = {user}')
    data = {'email': user.email, 'password': user.password}
    print(f'data = {data}')
    response = client.post(f'{URL}api/v1/user/login/', data=data, format='json')
    print(f'response = {response}')
    assert response.status_code == 200
    print(f'response.json() = {response.json()}')
    response_data = response.json()
    users = UserModel.objects.all()
    print(f'users = {users}')
    assert response_data['Token'] == 'uiduihja'
