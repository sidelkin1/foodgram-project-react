from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest

User = get_user_model()


class Test00UserRegistration:
    url_users = reverse('api:user-list')
    url_token = reverse('api:login')
    url_password = reverse('api:user-set-password')
    url_logout = reverse('api:logout')

    @pytest.mark.django_db(transaction=True)
    def test_01_nodata_signup(self, client):
        request_type = 'POST'
        response = client.post(self.url_users)

        assert response.status_code != 404, (
            f'Страница `{self.url_users}` не найдена, проверьте этот адрес в *urls.py*'
        )
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_users}` без параметров '
            f'не создается пользователь и возвращается статус {code}'
        )
        response_json = response.json()
        empty_fields = ('email', 'username', 'password', 'first_name', 'last_name')
        for field in empty_fields:
            assert field in response_json and isinstance(response_json[field], list), (
                f'Проверьте, что при {request_type} запросе `{self.url_users}` без параметров '
                f'в ответе есть сообщение об отсутствующем поле `{field}`'
            )

    @pytest.mark.django_db(transaction=True)
    def test_02_invalid_data_signup(self, client):
        invalid_fields = {
            'username': '(^!^)',
            'email': 'invalid_email',
            'password': '12345'
        }
        data = {
            'email': 'user@ya.ru',
            'password': 'B;tdcr64',
            'username': 'user',
            'first_name': 'Vasya',
            'last_name': 'Pupkin',
        }
        request_type = 'POST'

        for field, invalid_value in invalid_fields.items():
            invalid_data = data.copy()
            invalid_data[field] = invalid_value
            response = client.post(self.url_users, data=invalid_data)

            assert response.status_code != 404, (
                f'Страница `{self.url_users}` не найдена, проверьте этот адрес в *urls.py*'
            )
            code = 400
            assert response.status_code == code, (
                f'Проверьте, что при {request_type} запросе `{self.url_users}` с невалидными данными '
                f'не создается пользователь и возвращается статус {code}'
            )

            response_json = response.json()
            assert field in response_json.keys() and isinstance(response_json[field], list), (
                f'Проверьте, что при {request_type} запросе `{self.url_users}` с невалидными параметрами, '
                f'в ответе есть сообщение о том, что поле `{field}` заполенено неправильно'
            )

    @pytest.mark.django_db(transaction=True)
    def test_03_valid_data_user_signup(self, client):
        valid_data = {
            'email': 'user@ya.ru',
            'password': 'B;tdcr64',
            'username': 'user',
            'first_name': 'Vasya',
            'last_name': 'Pupkin',
        }
        request_type = 'POST'
        response = client.post(self.url_users, data=valid_data)

        assert response.status_code != 404, (
            f'Страница `{self.url_users}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_users}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )

        response_json = response.json()
        user_id = response_json.pop('id')
        valid_data.pop('password')
        assert isinstance(response_json, dict) and response_json == valid_data, (
            f'Проверьте, что при {request_type} запросе `{self.url_users}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )
        assert user_id is not None, (
            f'Проверьте, что при {request_type} запросе `{self.url_users}` с валидными данными '
            f'создается пользователь с непустым `id` и возвращается статус {code}'
        )

        new_user = User.objects.filter(id=user_id)
        assert new_user.exists(), (
            f'Проверьте, что при {request_type} запросе `{self.url_users}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )

        instance = User.objects.get(id=user_id)
        for field, value in valid_data.items():
            assert getattr(instance, field, None) == value, (
                f'Проверьте, что при {request_type} запросе `{self.url_users}` с валидными данными '
                f'создается пользователь с полем `{field}` и возвращается статус {code}'
            )

        new_user.delete()

    @pytest.mark.django_db(transaction=True)
    def test_04_obtain_token_invalid_data(self, client):

        request_type = 'POST'
        response = client.post(self.url_token)
        assert response.status_code != 404, (
            f'Страница `{self.url_token}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_token}` без параметров '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'password': 12345
        }
        response = client.post(self.url_token, data=invalid_data)
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_token}` без email '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'email': 'nonexisting@mail.fake',
            'password': 12345
        }
        response = client.post(self.url_token, data=invalid_data)
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_token}` с несуществующим email '
            f'возвращается статус {code}'
        )

        valid_data = {
            'email': 'user@ya.ru',
            'password': 'B;tdcr64',
            'username': 'user',
            'first_name': 'Vasya',
            'last_name': 'Pupkin',
        }
        response = client.post(self.url_users, data=valid_data)
        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_users}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )

        invalid_data = {
            'email': valid_data['email'],
            'password': 12345
        }
        response = client.post(self.url_token, data=invalid_data)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_token}` с валидным email, '
            f'но невалидным password, возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_registration_same_email_restricted(self, client):
        request_type = 'POST'

        valid_data = {
            'email': 'user@ya.ru',
            'password': 'B;tdcr64',
            'username': 'user',
            'first_name': 'Vasya',
            'last_name': 'Pupkin',
        }
        duplicate_data = valid_data.copy()

        response = client.post(self.url_users, data=valid_data)
        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_users}` '
            f'можно создать пользователя с валидными данными и возвращается статус {code}'
        )

        duplicate_data |= {
            'email': valid_data['email'],
            'username': 'user2',
        }
        response = client.post(self.url_users, data=duplicate_data)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_users}` нельзя создать '
            f'пользователя, email которого уже зарегистрирован, и возвращается статус {code}'
        )
        duplicate_data |= {
            'email': 'user2@ya.ru',
            'username': valid_data['username'],
        }
        response = client.post(self.url_users, data=duplicate_data)
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_users}` нельзя создать '
            f'пользователя, username которого уже зарегистрирован, и возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_registration_set_password(self, client, user, user_client, common_password):
        password_data = {
            'new_password': 'B;tdcr64',
            'current_password': common_password,
        }

        response = client.post(self.url_password, data=password_data)
        assert response.status_code != 404, (
            f'Страница `{self.url_password}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_password}` для неавторизованного пользователя '
            f'возвращается статус {code}'
        )

        response = user_client.post(self.url_password, data=password_data)
        code = 204
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_password}` для авторизованного пользователя '
            f'возвращается статус {code}'
        )

        signin_data = {
            'email': user.email,
            'password': password_data['new_password'],
        }
        response = client.post(self.url_token, data=signin_data)
        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_token}` с новым паролем '
            f'возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_registration_password_invalid_data(self, user_client, common_password):
        response = user_client.post(self.url_password)
        assert response.status_code != 404, (
            f'Страница `{self.url_password}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_password}` без параметров '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'new_password': 'B;tdcr64',
        }
        response = user_client.post(self.url_password, data=invalid_data)
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_password}` без current_password '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'new_password': 'B;tdcr64',
            'current_password': '111111',
        }
        response = user_client.post(self.url_password, data=invalid_data)
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_password}` с неправильным current_password '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'new_password': common_password,
            'current_password': common_password,
        }
        response = user_client.post(self.url_password, data=invalid_data)
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_password}` с неправильным new_password '
            f'возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_registration_del_token(self, client, user_client):
        response = client.post(self.url_logout)
        assert response.status_code != 404, (
            f'Страница `{self.url_password}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_logout}` для неавторизованного пользователя '
            f'возвращается статус {code}'
        )

        response = user_client.post(self.url_logout)
        code = 204
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_logout}` для авторизованного пользователя '
            f'возвращается статус {code}'
        )
