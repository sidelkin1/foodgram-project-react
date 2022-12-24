from collections import defaultdict

from django.urls import reverse

import pytest

from .common import check_instances, reverse_query


class Test03TagsIngredientsAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_tags_get(self, client, tags):
        url = reverse('api:tag-list')
        response = client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
        )

        data = response.json()
        fields = {
            'id': (None, True),
            'name': (None, True),
            'color': (None, True),
            'slug': (None, True),
        }
        check_instances(tags, data, fields, url, 'GET', 'JSON')

    @pytest.mark.django_db(transaction=True)
    def test_02_ingredients_get(self, client, ingredients):
        url = reverse('api:ingredient-list')
        response = client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
        )

        data = response.json()
        fields = {
            'id': (None, True),
            'name': (None, True),
            'measurement_unit': (None, True),
        }
        check_instances(ingredients, data, fields, url, 'GET', 'JSON')

    @pytest.mark.django_db(transaction=True)
    def test_03_ingredients_search_name(self, client, ingredients):
        letters = defaultdict(list)
        for ingredient in ingredients:
            letters[ingredient.name[0]].append(ingredient)

        for letter, grouped_ingredients in letters.items():
            url = reverse_query('api:ingredient-list', query_kwargs={'name': letter})
            response = client.get(url)
            assert response.status_code != 404, (
                f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
            )

            code = 200
            assert response.status_code == code, (
                f'Проверьте, что при GET запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
            )

            data = response.json()
            fields = {
                'id': (None, True),
                'name': (None, True),
                'measurement_unit': (None, True),
            }
            check_instances(grouped_ingredients, data, fields, url, 'GET', 'JSON')
