from django.contrib.auth import get_user_model
from django.db import transaction

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (Favorite, Ingredient, Purchase, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscription

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        required=True,
        validators=(UniqueValidator(queryset=User.objects.all()),),
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'password', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Subscription.objects.filter(user=user, author=obj).exists()
        )


class RecipePreviewSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context['request']
        queryset = Recipe.objects.filter(author=obj)
        if limit := request.GET.get('recipes_limit'):
            queryset = queryset[:int(limit)]
        return RecipePreviewSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredient_list',
        read_only=True,
        many=True,
    )
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_in_shopping_cart', 'is_favorited')

    def validate(self, data):
        data['ingredients'] = self.initial_data['ingredients']
        data['tags'] = self.initial_data['tags']
        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._set_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self._set_ingredients(instance, ingredients)
        instance.save()
        return instance

    def _set_ingredients(self, recipe, ingredients):
        objs = (RecipeIngredient(recipe=recipe,
                                 ingredient_id=ingredient['id'],
                                 amount=ingredient['amount'])
                for ingredient in ingredients)
        RecipeIngredient.objects.bulk_create(objs)

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Purchase.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=obj).exists()
        )
