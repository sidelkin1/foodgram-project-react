from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework_csv import renderers

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.order_by('id')


class MyUserRenderer(renderers.CSVRenderer):
    header = ['first', 'last', 'email']


@api_view(['GET'])
@renderer_classes((MyUserRenderer,))
def my_view(request):
    users = User.objects.filter(is_active=True)
    content = [{'first': user.first_name,
                'last': user.last_name,
                'email': user.email}
               for user in users]
    return Response(content)
