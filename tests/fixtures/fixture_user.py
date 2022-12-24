import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


@pytest.fixture
def user_data():
    return {
        'email': 'user@ya.ru',
        'password': 'B;tdcr64',
        'username': 'user',
        'first_name': 'Vasya',
        'last_name': 'Pupkin',
    }


@pytest.fixture
def common_password():
    return '1234567'


@pytest.fixture
def user_superuser(django_user_model, common_password):
    return django_user_model.objects.create_superuser(
        username='TestSuperuser',
        email='testsuperuser@yamdb.fake',
        password=common_password,
        firts_name='Super',
        last_name='Man',
    )


@pytest.fixture
def user(django_user_model, common_password):
    return django_user_model.objects.create_user(
        username='TestUser',
        email='testuser@yamdb.fake',
        password=common_password,
        first_name='Vasya',
        last_name='Pupkin',
    )


@pytest.fixture
def token_user_superuser(user_superuser):
    return Token.objects.create(user=user_superuser)


@pytest.fixture
def user_superuser_client(token_user_superuser):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_user_superuser}')
    return client


@pytest.fixture
def token_user(user):
    return Token.objects.create(user=user)


@pytest.fixture
def user_client(token_user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_user}')
    return client
