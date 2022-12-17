from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest

from .common import reverse_query

User = get_user_model()


class Test01UserAPI:
    @pytest.mark.django_db(transaction=True)
    def test_01_users_not_authenticated(self, client):
        url = reverse('api:user-list')
        response = client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` без токена авторизации возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_users_id_not_authenticated(self, client, user):
        url = reverse('api:user-detail', kwargs={'id': user.id})
        response = client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` без токена авторизации возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_users_me_not_authenticated(self, client):
        url = reverse('api:user-me')
        response = client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` без токена авторизации возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_users_get_anon(self, client, recipes):
        url = reverse('api:user-list')
        response = client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
        )

        data = response.json()
        for param in ('count', 'next', 'previous', 'results'):
            assert param in data, (
                f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
                'Не найден параметр `{param}`'
            )
        assert data['count'] == len(recipes), (
            f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
            'Значение параметра `count` не правильное'
        )
        assert type(data['results']) == list and len(data['results']) == len(recipes), (
            f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
            'Тип параметра `results` должен быть список'
        )

        for recipe, user in zip(recipes, data['results']):
            for field, value in user.items():
                assert (getattr(recipe.author, field, None) == value
                        if field != 'is_subscribed' else not value), (
                    f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
                    f'Значение поля *{field}* параметра `results` не правильное'
                )

    @pytest.mark.django_db(transaction=True)
    def test_05_users_get_auth(self, user_client):
        url = reverse('api:user-list')
        response = user_client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` для авторизованного пользователя возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_users_get_me(self, client, user_client):
        url = reverse('api:user-me')
        response = client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
        )
        response = user_client.get(url)
        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` для авторизованного пользователя возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_users_get_with_page_limit(self, client, recipes):
        for limit in range(1, len(recipes) + 1):
            url = reverse_query('api:user-list', query_kwargs={'limit': limit})
            response = client.get(url)
            assert response.status_code != 404, (
                f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
            )

            data = response.json()
            for param in ('count', 'results'):
                assert param in data, (
                    f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
                    'Не найден параметр `{param}`'
                )
            assert data['count'] == len(recipes), (
                f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
                'Значение параметра `count` не правильное'
            )
            assert type(data['results']) == list and len(data['results']) == limit, (
                f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
                f'Тип параметра `results` должен быть список с длиной {limit}'
            )
