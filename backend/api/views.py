from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, F, Sum

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Purchase, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscription

from . import filters, paginations, permissions, renderers, serializers
from .utils import get_exists_subquery

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = paginations.LimitPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.order_by('id')
        if self.action == 'subscriptions':
            return (
                queryset
                .filter(subscribers__user_id=user.id)
                .annotate(recipes_count=Count('recipes'))
            )
        subquery = get_exists_subquery(
            Subscription, user, 'is_subscribed', 'author'
        )
        return queryset.annotate(**subquery)

    def get_serializer_class(self):
        if self.action in ('subscriptions', 'subscribe'):
            return serializers.SubscriptionSerializer
        return super().get_serializer_class()

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @transaction.atomic
    @action(('post',), detail=True)
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        author = self.get_object()
        subscription = Subscription.objects.filter(user=user, author=author)
        if (user == author) or subscription.exists():
            return Response(
                {'errors': 'Ошибка подписки!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscription.objects.create(user=user, author=author)
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @subscribe.mapping.delete
    def del_subscribe(self, request, *args, **kwargs):
        user = request.user
        author = self.get_object()
        subscription = Subscription.objects.filter(user=user, author=author)
        if (user == author) or (not subscription.exists()):
            return Response(
                {'errors': 'Ошибка отписки!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = (filters.IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    permission_classes = (permissions.IsAuthorOrReadOnly,)
    pagination_class = paginations.LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.RecipeFilterSet

    def get_queryset(self):
        user = self.request.user
        subquery = get_exists_subquery(
            Purchase, user, 'is_in_shopping_cart', 'recipe'
        )
        subquery |= get_exists_subquery(
            Favorite, user, 'is_favorited', 'recipe'
        )
        return Recipe.objects.annotate(**subquery)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(('post',), detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        return self._add_object(Purchase, request.user)

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request, *args, **kwargs):
        return self._delete_object(Purchase, request.user)

    @action(('post',), detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        return self._add_object(Favorite, request.user)

    @favorite.mapping.delete
    def del_favorite(self, request, *args, **kwargs):
        return self._delete_object(Favorite, request.user)

    @transaction.atomic
    def _add_object(self, model, user):
        recipe = self.get_object()
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Ошибка добавления рецепта!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = serializers.RecipePreviewSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def _delete_object(self, model, user):
        recipe = self.get_object()
        obj = model.objects.filter(user=user, recipe=recipe)
        if not obj.exists():
            return Response(
                {'errors': 'Ошибка удаления рецепта!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, renderer_classes=(renderers.IngredientCSVRenderer,),
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredient_fields = {
            'Ингредиент': F('ingredient__name'),
            'Ед. изм.': F('ingredient__measurement_unit'),
        }
        amount_sum = {'Количество': Sum('amount')}
        content = list(
            RecipeIngredient.objects
            .filter(recipe__purchases__user=request.user)
            .values(**ingredient_fields)
            .annotate(**amount_sum)
        )
        return Response(content)

    def get_renderer_context(self):
        context = super().get_renderer_context()
        if self.action == 'download_shopping_cart':
            context['encoding'] = 'cp1251'
        return context
