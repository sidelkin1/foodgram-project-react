from django.urls import reverse

import pytest


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
        for tag, result in zip(tags, data):
            for field, value in result.items():
                assert getattr(tag, field, None) == value, (
                    f'Проверьте, что при GET запросе `{url}` возвращаете корректные данные. '
                    f'Значение параметра `{field}` не правильное'
                )

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
        for ingredient, result in zip(ingredients, data):
            for field, value in result.items():
                assert getattr(ingredient, field, None) == value, (
                    f'Проверьте, что при GET запросе `{url}` возвращаете корректные данные. '
                    f'Значение параметра `{field}` не правильное'
                )
