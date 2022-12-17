from django.urls import reverse

import pytest

from users.models import Subscription

from .common import reverse_query


class Test02SubscriptionAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_subscribe_auth(self, user, user_client, recipes):
        author = recipes[0].author
        url = reverse('api:user-subscribe', kwargs={'id': author.id})
        response = user_client.post(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для авторизованного пользователя возвращается статус {code}'
        )

        assert Subscription.objects.filter(user=user, author=author).exists(), (
            f'Проверьте, что при POST запросе `{url}` создалась запись в БД'
        )

        data = response.json()
        recipe = data.pop('recipes')[0]
        recipes_count = data.pop('recipes_count')
        for field, value in data.items():
            assert (getattr(author, field, None) == value
                    if field != 'is_subscribed' else value), (
                f'Проверьте, что при POST запросе `{url}` возвращаете корректные данные. '
                f'Значение поля *{field}* не правильное'
            )
        for field, value in recipe.items():
            model_value = getattr(recipes[0], field, None)
            assert (model_value == value if field != 'image'
                    else str(model_value) in value), (
                f'Проверьте, что при POST запросе `{url}` возвращаете корректные данные. '
                f'Значение поля *{field}* параметра `recipes` не правильное'
            )
        assert recipes_count == 1, (
            f'Проверьте, что при POST запросе `{url}` возвращаете корректные данные. '
            f'Значение поля *recipes_count* не правильное'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_subscribe_anon(self, client, recipes):
        author = recipes[0].author
        url = reverse('api:user-subscribe', kwargs={'id': author.id})
        response = client.post(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_subscribe_invalid_data(self, user, user_client, recipes):
        author = recipes[0].author
        url = reverse('api:user-subscribe', kwargs={'id': author.id})
        response = user_client.post(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для авторизованного пользователя возвращается статус {code}'
        )

        response = user_client.post(url)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` на повторную подписку возвращается статус {code}'
        )
        assert Subscription.objects.filter(user=user, author=author).count() == 1, (
            f'Проверьте, что при POST запросе `{url}` на повторную подписку не создалась запись в БД'
        )

        url = reverse('api:user-subscribe', kwargs={'id': user.id})
        response = user_client.post(url)
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` на самоподписку возвращается статус {code}'
        )
        assert not Subscription.objects.filter(user=user, author=user).exists(), (
            f'Проверьте, что при POST запросе `{url}` на самоподписку не создалась запись в БД'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_unsubscribe_auth(self, user, user_client, recipes):
        author = recipes[0].author
        url = reverse('api:user-subscribe', kwargs={'id': author.id})
        response = user_client.post(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для авторизованного пользователя возвращается статус {code}'
        )

        response = user_client.delete(url)
        code = 204
        assert response.status_code == code, (
            f'Проверьте, что при DELETE запросе `{url}` для авторизованного пользователя возвращается статус {code}'
        )
        assert not Subscription.objects.filter(user=user, author=author).exists(), (
            f'Проверьте, что при DELETE запросе `{url}` удалилась запись в БД'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_unsubscribe_anon(self, client, recipes):
        author = recipes[0].author
        url = reverse('api:user-subscribe', kwargs={'id': author.id})
        response = client.delete(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при DELETE запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_unsubscribe_invalid_data(self, user, user_client, recipes):
        author = recipes[0].author
        url = reverse('api:user-subscribe', kwargs={'id': author.id})
        response = user_client.delete(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при DELETE запросе `{url}` несуществующей подписки возвращается статус {code}'
        )

        url = reverse('api:user-subscribe', kwargs={'id': user.id})
        response = user_client.delete(url)
        assert response.status_code == code, (
            f'Проверьте, что при DELETE запросе `{url}` на самоотписку возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_subscriptions_get_auth(self, user_client, subscriptions):
        url = reverse('api:user-subscriptions')
        response = user_client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` для авторизованного пользователя возвращается статус {code}'
        )

        data = response.json()
        for param in ('count', 'next', 'previous', 'results'):
            assert param in data, (
                f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
                'Не найден параметр `{param}`'
            )
        assert data['count'] == len(subscriptions), (
            f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
            'Значение параметра `count` не правильное'
        )
        assert type(data['results']) == list and len(data['results']) == len(subscriptions), (
            f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
            'Тип параметра `results` должен быть список'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_subscriptions_get_anon(self, client):
        url = reverse('api:user-subscriptions')
        response = client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_09_subscriptions_get_with_recipes_limit(self, user_client, subscribed_recipes):
        for limit in range(1, len(subscribed_recipes) + 1):
            url = reverse_query('api:user-subscriptions', query_kwargs={'recipes_limit': limit})
            response = user_client.get(url)
            assert response.status_code != 404, (
                f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
            )

            data = response.json()
            for param in ('count', 'results'):
                assert param in data, (
                    f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
                    'Не найден параметр `{param}`'
                )
            assert data['count'] == 1, (
                f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
                'Значение параметра `count` не правильное'
            )
            assert type(data['results']) == list and len(data['results']) == 1, (
                f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
                f'Тип параметра `results` должен быть список с длиной 1'
            )

            result = data['results'][0]
            for param in ('recipes', 'recipes_count'):
                assert param in result, (
                    f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
                    f'Внутри `results` не найден параметр `{param}`'
                )
            assert type(result['recipes']) == list and len(result['recipes']) == limit, (
                f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
                f'Тип параметра `results.recipes` должен быть список с длиной {limit}'
            )
            assert result['recipes_count'] == len(subscribed_recipes), (
                f'Проверьте, что при GET запросе `{url}` возвращаете данные с пагинацией. '
                f'Значение параметра `results.recipes_count` не правильное'
            )
