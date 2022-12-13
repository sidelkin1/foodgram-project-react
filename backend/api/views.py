from django.contrib.auth import get_user_model
from django.db.models import F, Prefetch, Sum

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Purchase, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscription

from . import filters, mixins, paginations, permissions, renderers, serializers

User = get_user_model()


class CustomUserViewSet(UserViewSet, mixins.AddDeleteObjectMixin):
    pagination_class = paginations.LimitPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.with_is_subscribed(user)
        if self.action == 'subscriptions':
            return queryset.subscriptions(user)
        return queryset

    def get_serializer_class(self):
        if self.action in ('subscriptions', 'subscribe'):
            return serializers.SubscriptionSerializer
        return super().get_serializer_class()

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(('post',), detail=True)
    def subscribe(self, request, *args, **kwargs):
        return self.add_or_delete_object(
            Subscription,
            'author',
            'Ошибка подписки!'
        )

    @subscribe.mapping.delete
    def del_subscribe(self, request, *args, **kwargs):
        return self.add_or_delete_object(
            Subscription,
            'author',
            'Ошибка отписки!'
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = (filters.IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet, mixins.AddDeleteObjectMixin):
    permission_classes = (permissions.IsAuthorOrReadOnly,)
    pagination_class = paginations.LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.RecipeFilterSet

    def get_queryset(self):
        user = self.request.user
        return (
            Recipe.objects.with_is_fields(user)
            .prefetch_related(
                Prefetch(
                    'author',
                    queryset=User.objects.with_is_subscribed(user)
                )
            )
        )

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return serializers.RecipeReadSerializer
        if self.action in ('shopping_cart', 'favorite'):
            return serializers.RecipePreviewSerializer
        return serializers.RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(('post',), detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        return self.add_or_delete_object(
            Purchase,
            'recipe',
            'Ошибка добавления рецепта!'
        )

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request, *args, **kwargs):
        return self.add_or_delete_object(
            Purchase,
            'recipe',
            'Ошибка удаления рецепта!'
        )

    @action(('post',), detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        return self.add_or_delete_object(
            Favorite,
            'recipe',
            'Ошибка добавления рецепта!'
        )

    @favorite.mapping.delete
    def del_favorite(self, request, *args, **kwargs):
        return self.add_or_delete_object(
            Favorite,
            'recipe',
            'Ошибка удаления рецепта!'
        )

    @action(detail=False, renderer_classes=(renderers.IngredientCSVRenderer,),
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredient_fields = {
            'Ингредиент': F('ingredient__name'),
            'Ед. изм.': F('ingredient__measurement_unit'),
        }
        amount_sum = {'Количество': Sum('amount')}
        content = list(
            RecipeIngredient.objects.purchases(request.user)
            .values(**ingredient_fields)
            .annotate(**amount_sum)
        )
        return Response(content)

    def get_renderer_context(self):
        context = super().get_renderer_context()
        if self.action == 'download_shopping_cart':
            context['encoding'] = 'cp1251'
        return context
