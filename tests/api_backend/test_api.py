import pytest
from rest_framework.test import APIClient

@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
def test_account_register(client):
    data = {'email': 'newuser01@testmail.com', 'password': 'Jn9c2Xy6Qm1'}
    response = client.post('api/v1/user/register/', data=data, format='json')
    new_user = response.json()
    print(new_user)
    assert response.status_code == 201
    # assert new_user['email'] == 'newuser01@testmail.com'
