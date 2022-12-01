from django.contrib.auth import get_user_model
from django.db import transaction

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

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
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
        list_serializer_class = RecipePreviewListSerializer


class SubscriptionSerializer(UserSerializer):
    recipes = RecipePreviewSerializer(
        many=True,
        read_only=True,
        source='recipes.all'
    )
    recipes_count = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'recipes', 'recipes_count')


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
