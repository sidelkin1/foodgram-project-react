import datetime
import shutil
from pathlib import Path

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError

import pandas as pd
from sqlalchemy import create_engine


class Command(BaseCommand):
    help = 'Load Foodgram database'

    DB_URI = (
        'postgresql://'
        f'{settings.DATABASES["default"]["USER"]}'
        f':{settings.DATABASES["default"]["PASSWORD"]}'
        f'@{settings.DATABASES["default"]["HOST"]}'
        f':{settings.DATABASES["default"]["PORT"]}'
        f'/{settings.DATABASES["default"]["NAME"]}'
    )

    BASE_DIR = Path(settings.BASE_DIR)

    DB_TABLES = {
        'auth_user.csv': 'auth_user',
        'recipes_ingredient.csv': 'recipes_ingredient',
        'recipes_tag.csv': 'recipes_tag',
        'recipes_recipe.csv': 'recipes_recipe',
        'recipes_recipe_tags.csv': 'recipes_recipe_tags',
        'recipes_recipeingredient.csv': 'recipes_recipeingredient',
        'recipes_favorite.csv': 'recipes_favorite',
        'recipes_purchase.csv': 'recipes_purchase',
    }

    def handle(self, *args, **options):
        try:
            engine = create_engine(self.DB_URI)

            with engine.connect().execution_options(autocommit=True) as conn:
                self.stdout.write(
                    self.style.SUCCESS('Успешное подключение к БД')
                )

                for file_name, table_name in self.DB_TABLES.items():
                    self.stdout.write(
                        self.style.NOTICE(
                            f'Обработка таблицы {table_name}... '
                        ),
                        ending='',
                    )

                    path = self.BASE_DIR.joinpath('data', file_name)
                    df = pd.read_csv(path)

                    if table_name == 'auth_user':
                        df = df.assign(
                            password=make_password('12345'),
                            last_login=pd.NaT,
                            is_superuser=False,
                            is_staff=False,
                            is_active=True,
                            date_joined=datetime.datetime.now(),
                        )
                    elif table_name == 'recipes_recipe':
                        df = df.assign(pub_date=datetime.datetime.now())
                        path = self.BASE_DIR.joinpath('data')
                        media = self.BASE_DIR.joinpath('media', 'recipes')
                        media.mkdir(parents=True, exist_ok=True)
                        for image in path.glob('*.jpg'):
                            shutil.copy(image, media)
                    df.drop(columns='id', inplace=True)

                    df.to_sql(
                        name=table_name,
                        con=conn,
                        if_exists='append',
                        index=False,
                    )

                    self.stdout.write(
                        self.style.SUCCESS('OK')
                    )

        except Exception as error:
            raise CommandError(error) from error
        finally:
            engine.dispose()
