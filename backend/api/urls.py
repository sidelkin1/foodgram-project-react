from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register('users', views.CustomUserViewSet, basename='user')
router.register('tags', views.TagsViewSet, basename='tag')
router.register('ingredients', views.IngredientsViewSet, basename='ingredient')
router.register('recipes', views.RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('csv/', views.my_view, name='my_view')
]
