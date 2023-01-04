from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

from . import validators

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'password', 'first_name', 'last_name')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed')


class RecipePreviewListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        request = self.context['request']
        if limit := request.GET.get('recipes_limit'):
            data = data[:int(limit)]
        return super().to_representation(data)


class RecipePreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        list_serializer_class = RecipePreviewListSerializer


class SubscriptionSerializer(UserSerializer):
    recipes = RecipePreviewSerializer(
        many=True,
        read_only=True,
        source='recipes.all'
    )
    is_subscribed = serializers.ReadOnlyField()
    recipes_count = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='ingredient_list.all',
        read_only=True,
        many=True,
    )
    is_in_shopping_cart = serializers.ReadOnlyField()
    is_favorited = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_in_shopping_cart', 'is_favorited')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = RecipeIngredientWriteSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')
        validators = (
            validators.DuplicateValidator(
                source='tags.id',
            ),
            validators.DuplicateValidator(
                source='ingredients.id.id',
            ),
        )

    def to_representation(self, instance):
        if self.context['request'].method == 'POST':
            # Явно делаем запрос в БД, чтобы добавить нужные
            # доп. поля для сериализатора (см. реализацию 'get_queryset')
            queryset = self.context['view'].get_queryset()
            instance = get_object_or_404(queryset, id=instance.id)
        return RecipeReadSerializer(instance).data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.add(*tags)
        self._add_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.tags.set(tags, clear=True)
        instance.ingredients.clear()
        self._add_ingredients(instance, ingredients)
        instance.save()
        return instance

    def _add_ingredients(self, recipe, ingredients):
        objs = (RecipeIngredient(recipe=recipe,
                                 ingredient=ingredient['id'],
                                 amount=ingredient['amount'])
                for ingredient in ingredients)
        RecipeIngredient.objects.bulk_create(objs)
