from django.urls import reverse

import pytest
from rest_framework.test import APIClient

from recipes.models import Favorite, Purchase, Recipe

from .common import (check_attributes, check_pagination_fields,
                     check_recipe_data, check_recipes, reverse_query)


class Test04RecipeAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_recipes_get_anon(self, client, complete_recipes):
        url = reverse('api:recipe-list')
        response = client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
        )

        data = response.json()
        check_pagination_fields(data, len(complete_recipes), url)
        check_recipes(complete_recipes, data['results'], url, 'GET', 'results',
                      'results.author', 'results.tags', 'results.ingredients',
                      False, False, False)

    @pytest.mark.django_db(transaction=True)
    def test_02_recipes_post_anon(self, client, recipe_data, recipes):
        url = reverse('api:recipe-list')
        response = client.post(url, data=recipe_data, format='json')
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_recipes_post_auth(self, user, user_client, recipe_data, recipes):
        url = reverse('api:recipe-list')
        response = user_client.post(url, data=recipe_data, format='json')
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для авторизованного пользователя возвращается статус {code}'
        )

        data = response.json()
        queryset = Recipe.objects.filter(id=data.get('id'))
        assert Recipe.objects.count() == len(recipes) + 1 and queryset.exists(), (
            f'Проверьте, что при POST запросе `{url}` появилась новая запись в БД'
        )
        new_recipe = queryset.first()
        check_recipes([new_recipe], [data], url, 'POST', 'JSON',
                      'author', 'tags', 'ingredients',
                      False, False, False)
        check_recipe_data(recipe_data, data, url, 'POST', 'JSON', 'tags', 'ingredients')

    @pytest.mark.django_db(transaction=True)
    def test_04_recipes_patch_anon_or_nonauthor(self, client, user_client, recipe_data, tags, ingredients, recipes):
        url = reverse('api:recipe-detail', kwargs={'pk': recipes[0].id})
        response = client.patch(url, data=recipe_data, format='json')
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при PATCH запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
        )

        code = 403
        response = user_client.patch(url, data=recipe_data, format='json')
        assert response.status_code == code, (
            f'Проверьте, что при PATCH запросе `{url}` для авторизованного неавтора возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_recipes_patch_author(self, recipe_data, recipes):
        url = reverse('api:recipe-detail', kwargs={'pk': recipes[0].id})
        author_client = APIClient()
        author_client.force_authenticate(user=recipes[0].author)
        response = author_client.patch(url, data=recipe_data, format='json')
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при PATCH запросе `{url}` для авторизованного автора возвращается статус {code}'
        )

        data = response.json()
        queryset = Recipe.objects.filter(id=recipes[0].id)
        assert Recipe.objects.count() == len(recipes) and queryset.exists(), (
            f'Проверьте, что при PATCH запросе `{url}` не появилась новая запись в БД'
        )
        new_recipe = queryset.first()
        check_recipes([new_recipe], [data], url, 'POST', 'JSON',
                      'author', 'tags', 'ingredients',
                      False, False, False)
        check_recipe_data(recipe_data, data, url, 'PATCH', 'JSON', 'tags', 'ingredients')

    @pytest.mark.django_db(transaction=True)
    def test_06_recipes_delete_anon_or_nonauthor(self, client, user_client, recipes):
        url = reverse('api:recipe-detail', kwargs={'pk': recipes[0].id})
        response = client.delete(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при DELETE запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
        )

        code = 403
        response = user_client.delete(url)
        assert response.status_code == code, (
            f'Проверьте, что при DELETE запросе `{url}` для авторизованного неавтора возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_recipes_delete_author(self, recipes):
        url = reverse('api:recipe-detail', kwargs={'pk': recipes[0].id})
        author_client = APIClient()
        author_client.force_authenticate(user=recipes[0].author)
        response = author_client.delete(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 204
        assert response.status_code == code, (
            f'Проверьте, что при DELETE запросе `{url}` для авторизованного автора возвращается статус {code}'
        )

        queryset = Recipe.objects.filter(id=recipes[0].id)
        assert Recipe.objects.count() == len(recipes) - 1 and not queryset.exists(), (
            f'Проверьте, что при DELETE запросе `{url}` удалилась запись в БД'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_recipes_favorite_post_auth(self, user, user_client, recipes):
        url = reverse('api:recipe-favorite', kwargs={'pk': recipes[0].id})
        response = user_client.post(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для авторизованного автора возвращается статус {code}'
        )

        assert Favorite.objects.filter(recipe=recipes[0], user=user).exists(), (
            f'Проверьте, что при POST запросе `{url}` создалась запись в БД'
        )

        data = response.json()
        fields = {
            'id': (None, True),
            'name': (None, True),
            'image': (None, True),
            'cooking_time': (None, True),
        }
        check_attributes(recipes[0], data, fields, url, http_method='POST')

        response = user_client.post(url)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при повторном POST запросе `{url}` для авторизованного автора возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_09_recipes_favorite_post_anon(self, client, recipes):
        url = reverse('api:recipe-favorite', kwargs={'pk': recipes[0].id})
        response = client.post(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для неавторизованного автора возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_10_recipes_favorite_delete_auth(self, user, user_client, favorited_recipes):
        url = reverse('api:recipe-favorite', kwargs={'pk': favorited_recipes[0].id})
        response = user_client.delete(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 204
        assert response.status_code == code, (
            f'Проверьте, что при DELETE запросе `{url}` для авторизованного автора возвращается статус {code}'
        )

        assert not Favorite.objects.filter(recipe=favorited_recipes[0], user=user).exists(), (
            f'Проверьте, что при DELETE запросе `{url}` удалилась запись в БД'
        )

        response = user_client.delete(url)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при повторном DELETE запросе `{url}` для авторизованного автора возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_11_recipes_favorite_delete_anon(self, client, favorited_recipes):
        url = reverse('api:recipe-favorite', kwargs={'pk': favorited_recipes[0].id})
        response = client.delete(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при DELETE запросе `{url}` для неавторизованного автора возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_12_recipes_purchase_post_auth(self, user, user_client, recipes):
        url = reverse('api:recipe-shopping-cart', kwargs={'pk': recipes[0].id})
        response = user_client.post(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для авторизованного автора возвращается статус {code}'
        )

        assert Purchase.objects.filter(recipe=recipes[0], user=user).exists(), (
            f'Проверьте, что при POST запросе `{url}` создалась запись в БД'
        )

        data = response.json()
        fields = {
            'id': (None, True),
            'name': (None, True),
            'image': (None, True),
            'cooking_time': (None, True),
        }
        check_attributes(recipes[0], data, fields, url, http_method='POST')

        response = user_client.post(url)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при повторном POST запросе `{url}` для авторизованного автора возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_13_recipes_purchase_post_anon(self, client, recipes):
        url = reverse('api:recipe-shopping-cart', kwargs={'pk': recipes[0].id})
        response = client.post(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{url}` для неавторизованного автора возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_14_recipes_purchase_delete_auth(self, user, user_client, purchased_recipes):
        url = reverse('api:recipe-shopping-cart', kwargs={'pk': purchased_recipes[0].id})
        response = user_client.delete(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 204
        assert response.status_code == code, (
            f'Проверьте, что при DELETE запросе `{url}` для авторизованного автора возвращается статус {code}'
        )

        assert not Purchase.objects.filter(recipe=purchased_recipes[0], user=user).exists(), (
            f'Проверьте, что при DELETE запросе `{url}` удалилась запись в БД'
        )

        response = user_client.delete(url)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при повторном DELETE запросе `{url}` для авторизованного автора возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_15_recipes_purchase_delete_anon(self, client, purchased_recipes):
        url = reverse('api:recipe-shopping-cart', kwargs={'pk': purchased_recipes[0].id})
        response = client.delete(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 401
        assert response.status_code == code, (
            f'Проверьте, что при DELETE запросе `{url}` для неавторизованного автора возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_16_recipes_filter_purchase(self, user_client, recipes, purchased_recipes):
        url = reverse_query('api:recipe-list', query_kwargs={'is_in_shopping_cart': 1})
        response = user_client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` для авторизованного пользователя возвращается статус {code}'
        )

        data = response.json()
        check_pagination_fields(data, len(purchased_recipes), url)
        check_recipes(purchased_recipes, data['results'], url, 'GET', 'results',
                      'results.author', 'results.tags', 'results.ingredients',
                      False, True, False)

    @pytest.mark.django_db(transaction=True)
    def test_17_recipes_filter_favorite(self, user_client, recipes, favorited_recipes):
        url = reverse_query('api:recipe-list', query_kwargs={'is_favorited': 1})
        response = user_client.get(url)
        assert response.status_code != 404, (
            f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при GET запросе `{url}` для авторизованного пользователя возвращается статус {code}'
        )

        data = response.json()
        check_pagination_fields(data, len(favorited_recipes), url)
        check_recipes(favorited_recipes, data['results'], url, 'GET', 'results',
                      'results.author', 'results.tags', 'results.ingredients',
                      False, False, True)

    @pytest.mark.django_db(transaction=True)
    def test_18_recipes_filter_author(self, client, recipes):
        for recipe in recipes:
            url = reverse_query('api:recipe-list', query_kwargs={'author': recipe.author.id})
            response = client.get(url)
            assert response.status_code != 404, (
                f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
            )

            code = 200
            assert response.status_code == code, (
                f'Проверьте, что при GET запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
            )

            data = response.json()
            check_pagination_fields(data, 1, url)
            check_recipes([recipe], data['results'], url, 'GET', 'results',
                          'results.author', 'results.tags', 'results.ingredients',
                          False, False, False)

    @pytest.mark.django_db(transaction=True)
    def test_19_recipes_filter_tags(self, client, complete_recipes, tags):
        for limit in range(1, len(tags) + 1):
            query_kwargs = {'tags': [tag.slug for tag in tags[:limit]]}
            url = reverse_query('api:recipe-list', query_kwargs=query_kwargs, doseq=True)
            response = client.get(url)
            assert response.status_code != 404, (
                f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
            )

            code = 200
            assert response.status_code == code, (
                f'Проверьте, что при GET запросе `{url}` для неавторизованного пользователя возвращается статус {code}'
            )

            data = response.json()
            check_pagination_fields(data, limit, url)
            check_recipes(complete_recipes[:limit], data['results'], url, 'GET', 'results',
                          'results.author', 'results.tags', 'results.ingredients',
                          False, False, False)
