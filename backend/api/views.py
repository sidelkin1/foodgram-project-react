from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, renderer_classes
from rest_framework.response import Response
from rest_framework_csv import renderers
from users.models import Subscription

from . import serializers, permissions

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.order_by('id')

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'subscriptions':
            user = self.request.user
            subscriptions = user.subscriptions.values('author')
            queryset = queryset.filter(id__in=subscriptions)
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


class MyUserRenderer(renderers.CSVRenderer):
    header = ['first', 'last', 'email']


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    permission_classes = (permissions.IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@api_view(['GET'])
@renderer_classes((MyUserRenderer,))
def my_view(request):
    users = User.objects.filter(is_active=True)
    content = [{'first': user.first_name,
                'last': user.last_name,
                'email': user.email}
               for user in users]
    return Response(content)
