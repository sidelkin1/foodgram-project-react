from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Count, F, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce

from api.utils import get_exists_subquery


class UserQuerySet(models.QuerySet):
    def subscriptions(self, user):
        return self.filter(subscribers__user_id=user.id)

    def with_is_subscribed(self, user):
        subquery = get_exists_subquery(
            Subscription, user, 'is_subscribed', 'author'
        )
        return self.annotate(**subquery)

    def with_recipes_count(self):
        # Почему не сделан *обычный* 'annotate'?
        #   annotate(recipes_count=Coalesce(Count('recipes'), 0))
        # Делаем через подзапрос, чтобы
        # 1) не возникали конфликты с другими *обычными* 'annotate'
        # 2) не нарушалась сортировка записей в БД
        subquery = Subquery(
            User.objects
            .filter(pk=OuterRef('pk'))
            .annotate(recipes_count=Coalesce(Count('recipes'), 0))
            .values('recipes_count')
        )
        return self.annotate(recipes_count=subquery)


class CustomUserManager(UserManager.from_queryset(UserQuerySet)):
    """
    Необходим для успешной миграции. Если просто написать в модели User
        objects = UserManager.from_queryset(UserQuerySet)()
    то возникает ошибка
        Please note that you need to inherit from managers you dynamically
        generated with 'from_queryset()'.
    """


class User(AbstractUser):
    objects = CustomUserManager()

    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        help_text='Введите адрес email',
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        help_text='Введите имя пользователя',
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        help_text='Введите фамилию пользователя',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription',
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='prevent_self_follow',
            ),
        )
