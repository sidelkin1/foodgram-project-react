from django.db import IntegrityError, transaction

from rest_framework import status
from rest_framework.response import Response


class AddDeleteObjectMixin:

    @transaction.atomic
    def add_or_delete_object(self, model, field, error_message):
        user = self.request.user
        instance = self.get_object()

        if self.request.method == 'POST':
            try:
                model.objects.create(user=user, **{field: instance})
            except IntegrityError:
                return Response(
                    {'errors': error_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Повторно инстанцируем объект для учета изменений в БД
            serializer = self.get_serializer(self.get_object())
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            obj = model.objects.filter(user=user, **{field: instance})
            if not obj.exists():
                return Response(
                    {'errors': error_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'Недопустимый метод!'},
            status=status.HTTP_400_BAD_REQUEST
        )
