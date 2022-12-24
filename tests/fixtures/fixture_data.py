from string import ascii_lowercase

from django.contrib.auth import get_user_model

import pytest
from mixer.backend.django import mixer as _mixer

from recipes.models import (Favorite, Ingredient, Purchase, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscription

User = get_user_model()


@pytest.fixture
def mixer():
    return _mixer


@pytest.fixture
def recipes(mixer):
    recipes = mixer.cycle(3).blend(Recipe)
    return list(
        Recipe.objects.filter(id__in=(recipe.id for recipe in recipes))
    )


@pytest.fixture
def authors(recipes):
    return list(
        User.objects.filter(id__in=(recipe.author.id for recipe in recipes))
    )


@pytest.fixture
def tags(mixer):
    tags = mixer.cycle(3).blend(
        Tag,
        name=mixer.sequence('tag_{0}'),
        color=mixer.sequence('#FFFFF{0}'),
    )
    return list(
        Tag.objects.filter(id__in=(tag.id for tag in tags))
    )


@pytest.fixture
def ingredients(mixer):
    ingredients = mixer.cycle(3).blend(
        Ingredient,
        name=mixer.sequence(
            lambda c: ascii_lowercase[c % len(ascii_lowercase)] * 3 + str(c)
        ),
        measurement_unit=mixer.sequence('unit_{0}'),
    )
    return list(
        Ingredient.objects.filter(
            id__in=(ingredient.id for ingredient in ingredients)
        )
    )


@pytest.fixture
def complete_recipes(mixer, recipes, tags, ingredients):
    mixer.cycle(3).blend(
        RecipeIngredient,
        recipe=(recipe for recipe in recipes),
        ingredient=(ingredient for ingredient in ingredients),
    )
    for recipe, tag in zip(recipes, tags):
        recipe.tags.add(tag)
    return recipes


@pytest.fixture
def subscriptions(mixer, user, authors):
    mixer.cycle(len(authors)).blend(
        Subscription,
        user=user,
        author=(author for author in authors),
    )
    return [{
        'author': author,
        'recipes': list(Recipe.objects.filter(author=author)),
    } for author in authors]


@pytest.fixture
def subscribed_recipes(mixer, user):
    author = mixer.blend(User)
    mixer.blend(Subscription, user=user, author=author)
    recipes = mixer.cycle(3).blend(Recipe, author=author)
    return list(
        Recipe.objects.filter(id__in=(recipe.id for recipe in recipes))
    )


@pytest.fixture
def favorited_recipes(mixer, user):
    recipes = mixer.cycle(3).blend(Recipe)
    mixer.cycle(len(recipes)).blend(
        Favorite,
        recipe=(recipe for recipe in recipes),
        user=user,
    )
    return list(
        Recipe.objects.filter(id__in=(recipe.id for recipe in recipes))
    )


@pytest.fixture
def purchased_recipes(mixer, user):
    recipes = mixer.cycle(3).blend(Recipe)
    mixer.cycle(len(recipes)).blend(
        Purchase,
        recipe=(recipe for recipe in recipes),
        user=user,
    )
    return list(
        Recipe.objects.filter(id__in=(recipe.id for recipe in recipes))
    )


@pytest.fixture
def recipe_data(tags, ingredients):
    return {
        'ingredients': [
            {'id': ingredient.id, 'amount': ingredient.id * 2}
            for ingredient in ingredients
        ],
        'tags': [tag.id for tag in tags],
        'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMA'
                  'AABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAA'
                  'OxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='),
        'name': 'Name',
        'text': 'Text',
        'cooking_time': 1
    }
