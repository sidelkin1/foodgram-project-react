from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest

User = get_user_model()


class Test00UserRegistration:

    @pytest.mark.django_db(transaction=True)
    def test_01_nodata_signup(self, client):
        url = reverse('api:user-list')
        response = client.post(url)

        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` без параметров '
            f'не создается пользователь и возвращается статус {code}'
        )
        response_json = response.json()
        empty_fields = ('email', 'username', 'password', 'first_name', 'last_name')
        for field in empty_fields:
            assert field in response_json and isinstance(response_json[field], list), (
                f'Проверьте, что при POST запросе `{url}` без параметров '
                f'в ответе есть сообщение об отсутствующем поле `{field}`'
            )

    @pytest.mark.django_db(transaction=True)
    def test_02_invalid_data_signup(self, client, user_data):
        url = reverse('api:user-list')
        invalid_fields = {
            'username': '(^!^)',
            'email': 'invalid_email',
            'password': '12345'
        }

        for field, invalid_value in invalid_fields.items():
            invalid_data = user_data.copy()
            invalid_data[field] = invalid_value
            response = client.post(url, data=invalid_data, format='json')

            assert response.status_code != 404, (
                f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
            )
            code = 400
            assert response.status_code == code, (
                f'Проверьте, что при POST запросе `{url}` с невалидными данными '
                f'не создается пользователь и возвращается статус {code}'
            )

            response_json = response.json()
            assert field in response_json.keys() and isinstance(response_json[field], list), (
                f'Проверьте, что при POST запросе `{url}` с невалидными параметрами, '
                f'в ответе есть сообщение о том, что поле `{field}` заполенено неправильно'
            )

    @pytest.mark.django_db(transaction=True)
    def test_03_valid_data_user_signup(self, client, user_data):
        url = reverse('api:user-list')
        response = client.post(url, data=user_data, format='json')

        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )

        response_json = response.json()
        user_id = response_json.pop('id')
        user_data.pop('password')
        assert isinstance(response_json, dict) and response_json == user_data, (
            f'Проверьте, что при POST запросе `{url}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )
        assert user_id is not None, (
            f'Проверьте, что при POST запросе `{url}` с валидными данными '
            f'создается пользователь с непустым `id` и возвращается статус {code}'
        )

        new_user = User.objects.filter(id=user_id)
        assert new_user.exists(), (
            f'Проверьте, что при POST запросе `{url}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )

        instance = User.objects.get(id=user_id)
        for field, value in user_data.items():
            assert getattr(instance, field, None) == value, (
                f'Проверьте, что при POST запросе `{url}` с валидными данными '
                f'создается пользователь с полем `{field}` и возвращается статус {code}'
            )

        new_user.delete()

    @pytest.mark.django_db(transaction=True)
    def test_04_obtain_token_invalid_data(self, client, user_data):
        url = reverse('api:login')
        response = client.post(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` без параметров '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'password': 12345
        }
        response = client.post(url, data=invalid_data, format='json')
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` без email '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'email': 'nonexisting@mail.fake',
            'password': 12345
        }
        response = client.post(url, data=invalid_data, format='json')
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` с несуществующим email '
            f'возвращается статус {code}'
        )

        url_signup = reverse('api:user-list')
        response = client.post(url_signup, data=user_data, format='json')
        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url_signup}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )

        invalid_data = {
            'email': user_data['email'],
            'password': 12345
        }
        response = client.post(url, data=invalid_data, format='json')
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` с валидным email, '
            f'но невалидным password, возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_registration_same_email_restricted(self, client, user_data):
        url = reverse('api:user-list')
        duplicate_data = user_data.copy()

        response = client.post(url, data=user_data, format='json')
        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` '
            f'можно создать пользователя с валидными данными и возвращается статус {code}'
        )

        duplicate_data |= {
            'email': user_data['email'],
            'username': 'user2',
        }
        response = client.post(url, data=duplicate_data, format='json')
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` нельзя создать '
            f'пользователя, email которого уже зарегистрирован, и возвращается статус {code}'
        )
        duplicate_data |= {
            'email': 'user2@ya.ru',
            'username': user_data['username'],
        }
        response = client.post(url, data=duplicate_data, format='json')
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` нельзя создать '
            f'пользователя, username которого уже зарегистрирован, и возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_registration_set_password(self, client, user, user_client, common_password):
        url = reverse('api:user-set-password')
        password_data = {
            'new_password': 'B;tdcr64',
            'current_password': common_password,
        }

        response = client.post(url, data=password_data, format='json')
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для неавторизованного пользователя '
            f'возвращается статус {code}'
        )

        response = user_client.post(url, data=password_data, format='json')
        code = 204
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для авторизованного пользователя '
            f'возвращается статус {code}'
        )

        url_login = reverse('api:login')
        login_data = {
            'email': user.email,
            'password': password_data['new_password'],
        }
        response = client.post(url_login, data=login_data, format='json')
        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url_login}` с новым паролем '
            f'возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_registration_password_invalid_data(self, user_client, common_password):
        url = reverse('api:user-set-password')
        response = user_client.post(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` без параметров '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'new_password': 'B;tdcr64',
        }
        response = user_client.post(url, data=invalid_data, format='json')
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` без current_password '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'new_password': 'B;tdcr64',
            'current_password': '111111',
        }
        response = user_client.post(url, data=invalid_data, format='json')
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` с неправильным current_password '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'new_password': common_password,
            'current_password': common_password,
        }
        response = user_client.post(url, data=invalid_data, format='json')
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` с неправильным new_password '
            f'возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_registration_del_token(self, client, user_client):
        url = reverse('api:logout')
        response = client.post(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для неавторизованного пользователя '
            f'возвращается статус {code}'
        )

        response = user_client.post(url)
        code = 204
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для авторизованного пользователя '
            f'возвращается статус {code}'
        )
