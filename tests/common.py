from collections.abc import Mapping

from django.urls import reverse
from django.utils.http import urlencode

from recipes.models import RecipeIngredient


def reverse_query(view, urlconf=None, args=None, kwargs=None,
                  current_app=None, query_kwargs=None, doseq=False):
    base_url = reverse(view, urlconf=urlconf, args=args,
                       kwargs=kwargs, current_app=current_app)
    return (
        f'{base_url}?{urlencode(query_kwargs, doseq)}' if query_kwargs
        else base_url
    )


def get_attribute(instance, attr, default=None):
    if isinstance(instance, Mapping):
        return instance.get(attr, default)
    return getattr(instance, attr, default)


def check_attributes(instance, data, fields, url,
                     http_method='GET', data_name='JSON'):
    message = (
        f'Проверьте, что при {http_method} запросе `{url}` '
        f'возвращаете корректные данные. Внутри `{data_name}` '
        'поле `{}` не найдено или имеет неправильное значение'
    )
    for field, (default_value, need_check) in fields.items():
        value = get_attribute(instance, field, default_value)
        if not need_check:
            assert field in data, (
                message.format(field)
            )
        elif field == 'image':
            assert str(value) in data.get(field), (
                message.format(field)
            )
        else:
            assert value == data.get(field), (
                message.format(field)
            )


def check_pagination_fields(data, data_count, url,
                            http_method='GET', results_count=None):
    results_count = results_count or data_count
    message_header = (
        f'Проверьте, что при {http_method} запросе `{url}` '
        'возвращаете данные с пагинацией. '
    )
    for field in ('count', 'next', 'previous', 'results'):
        assert field in data, (
            f'{message_header}'
            f'Не найдено поле `{field}`'
        )
    assert data['count'] == data_count, (
        f'{message_header}'
        f'Значение поля `count` должно быть равно {data_count}'
    )
    assert (type(data['results']) == list
            and len(data['results']) == results_count), (
        f'{message_header}'
        f'Тип поля `results` должен быть список длиной {results_count}'
    )


def check_subscriptions(subscriptions, results, url,
                        http_method, author_name, recipe_name):
    author_fields = {
        'email': (None, True),
        'id': (None, True),
        'username': (None, True),
        'first_name': (None, True),
        'last_name': (None, True),
        'is_subscribed': (True, True),
        'recipes': (None, False),
    }
    recipe_fields = {
        'id': (None, True),
        'name': (None, True),
        'image': (None, True),
        'cooking_time': (None, True),
    }
    for subscription, result in zip(subscriptions, results):
        author, recipes = subscription['author'], subscription['recipes']
        author_fields |= {'recipes_count': (len(recipes), True)}
        check_attributes(
            author,
            result,
            author_fields,
            url,
            http_method=http_method,
            data_name=author_name
        )
        for recipe, recipe_result in zip(recipes, result['recipes']):
            check_attributes(
                recipe,
                recipe_result,
                recipe_fields,
                url,
                http_method=http_method,
                data_name=recipe_name
            )


def check_recipes(recipes, results, url, http_method, recipe_name,
                  author_name, tag_name, ingredient_name,
                  is_subsribed, is_in_shopping_cart, is_favorited):
    recipe_fields = {
        'id': (None, True),
        'author': (None, False),
        'name': (None, True),
        'image': (None, True),
        'text': (None, True),
        'cooking_time': (None, True),
        'is_in_shopping_cart': (is_in_shopping_cart, True),
        'is_favorited': (is_favorited, True),
        'tags': (None, False),
        'ingredients': (None, False),
    }
    author_fields = {
        'id': (None, True),
        'email': (None, True),
        'username': (None, True),
        'first_name': (None, True),
        'last_name': (None, True),
        'is_subscribed': (is_subsribed, True),
    }
    tag_fields = {
        'id': (None, True),
        'name': (None, True),
        'color': (None, True),
        'slug': (None, True),
    }
    ingredient_fields = {
        'id': (None, True),
        'name': (None, True),
        'measurement_unit': (None, True),
        'amount': (None, False),
    }

    for recipe, result in zip(recipes, results):
        check_attributes(
            recipe,
            result,
            recipe_fields,
            url,
            http_method=http_method,
            data_name=recipe_name
        )

        for field in ('tags', 'ingredients'):
            data_count = getattr(recipe, field).count()
            assert (type(result[field]) == list
                    and len(result[field]) == data_count), (
                f'Проверьте, что при {http_method} запросе `{url}` '
                'возвращаете корректные данные. '
                f'Тип параметра `results.{field}` '
                f'должен быть список длиной {data_count}'
            )

        check_attributes(
            recipe.author,
            result['author'],
            author_fields,
            url,
            http_method=http_method,
            data_name=author_name,
        )

        for tag, result_tag in zip(recipe.tags.all(), result['tags']):
            check_attributes(
                tag,
                result_tag,
                tag_fields,
                url,
                http_method=http_method,
                data_name=tag_name,
            )

        for ingredient, result_ingredient in zip(recipe.ingredients.all(),
                                                 result['ingredients']):
            check_attributes(
                ingredient,
                result_ingredient,
                ingredient_fields,
                url,
                http_method=http_method,
                data_name=ingredient_name,
            )

            amount = result_ingredient['amount']
            recipe_ingredient = (
                RecipeIngredient.objects.filter(recipe=recipe,
                                                ingredient=ingredient)
            )
            assert recipe_ingredient.exists(), (
                f'Проверьте, что при {http_method} запросе `{url}` '
                'возвращаете корректные данные. '
                f'Значение параметра `{ingredient_name}` не найдено в БД'
            )
            assert amount == recipe_ingredient.first().amount, (
                f'Проверьте, что при {http_method} запросе `{url}` '
                'возвращаете корректные данные. '
                f'Внутри `{ingredient_name}` поле `amount` '
                'имеет неправильное значение'
            )


def check_recipe_data(recipe_data, result, url, http_method,
                      recipe_name, tag_name, ingredient_name):
    recipe_fields = {
        'name': (None, True),
        'text': (None, True),
        'cooking_time': (None, True),
    }
    check_attributes(
        recipe_data,
        result,
        recipe_fields,
        url,
        http_method=http_method,
        data_name=recipe_name,
    )

    tag_fields = {
        'id': (None, True),
    }
    for tag, result_tag in zip(recipe_data['tags'], result['tags']):
        check_attributes(
            {'id': tag},
            result_tag,
            tag_fields,
            url,
            http_method=http_method,
            data_name=tag_name,
        )

    ingredient_fields = {
        'id': (None, True),
        'amount': (None, True),
    }
    for ingredient, result_ingredient in zip(recipe_data['ingredients'],
                                             result['ingredients']):
        check_attributes(
            ingredient,
            result_ingredient,
            ingredient_fields,
            url,
            http_method=http_method,
            data_name=ingredient_name,
        )


def check_instances(instances, data, fields, url, http_method, data_name):
    instances_count = len(instances)
    assert isinstance(data, list) and len(data) == instances_count, (
        f'Проверьте, что при {http_method} запросе `{url}` '
        f'возвращается список длиной {instances_count}'
    )
    for instance, result in zip(instances, data):
        check_attributes(
            instance,
            result,
            fields,
            url,
            http_method=http_method,
            data_name=data_name,
        )
