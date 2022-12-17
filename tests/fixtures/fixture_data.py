import pytest
from mixer.backend.django import mixer as _mixer


@pytest.fixture
def mixer():
    return _mixer


@pytest.fixture
def recipes(mixer):
    return mixer.cycle(3).blend('recipes.Recipe')


@pytest.fixture
def tags(mixer):
    return mixer.cycle(3).blend(
        'recipes.Tag',
        name=mixer.sequence('tag_{0}'),
        color=mixer.sequence('#FFFFF{0}'),
    )


@pytest.fixture
def ingredients(mixer):
    return mixer.cycle(3).blend(
        'recipes.Ingredient',
        name=mixer.sequence('ingredient_{0}'),
        measurement_unit=mixer.sequence('unit_{0}'),
    )


@pytest.fixture
def complete_recipes(mixer, recipes, tags, ingredients):
    mixer.cycle(3).blend(
        'recipes.RecipeIngredient',
        recipe=(recipe for recipe in recipes),
        ingredient=(ingredient for ingredient in ingredients),
    )
    for recipe in recipes:
        recipe.tags.add(*tags)
    return recipes


@pytest.fixture
def subscriptions(mixer, user, recipes):
    return mixer.cycle(len(recipes)).blend(
        'users.Subscription',
        user=user,
        author=(recipe.author for recipe in recipes),
    )


@pytest.fixture
def subscribed_recipes(mixer, user):
    author = mixer.blend('users.User')
    mixer.blend('users.Subscription', user=user, author=author)
    return mixer.cycle(3).blend('recipes.Recipe', author=author)
