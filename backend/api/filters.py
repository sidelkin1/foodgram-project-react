from django.contrib.auth import get_user_model

from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe

User = get_user_model()


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilterSet(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.AllValuesFilter()
    is_favorited = filters.BooleanFilter()
    is_in_shopping_cart = filters.BooleanFilter()

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
