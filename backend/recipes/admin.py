from django.contrib import admin

from . import models


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(models.RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    pass
