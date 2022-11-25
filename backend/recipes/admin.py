from django.contrib import admin

from . import models


class IngredientInline(admin.TabularInline):
    model = models.RecipeIngredient
    extra = 2


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInline,)


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
