from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

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
