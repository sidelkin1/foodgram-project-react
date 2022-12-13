![foodgram workflow](https://github.com/sidelkin1/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Проект Foodgram

Дипломный проект — сайт Foodgram, «Продуктовый помощник». Реализован онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Установка и запуск проекта

Клонировать репозиторий:

```
git clone https://github.com/sidelkin1/foodgram-project-react.git

```

Cоздать и запустить контейнеры:

```
cd foodgram-project-react/infra

docker-compose up -d --build
```

Выполнить миграции:

```
docker-compose exec backend python manage.py migrate
```

Заполнить базу данных:

```
docker-compose exec backend python manage.py loaddb
```

Собрать всю статику:

```
docker-compose exec backend python manage.py collectstatic --no-input
```

Создать суперпользователя:

```
docker-compose exec backend python manage.py createsuperuser  --no-input
```

Для удаления контейнеров выполнить команду:

```
cd foodgram-project-react/infra

docker-compose down -v
```

## Описание проекта

Информация об API и примеры запросов доступны по адресу
```
http://localhost/api/docs/
```

Главная страница доступна по адресу
```
http://localhost/recipes
```

Доступ к панели администратора осуществляется по адресу
```
http://localhost/admin
```

## Шаблон ENV-файла

| Переменная  | Пример значения | Описание |
|:---|:---|:---|
| `DB_ENGINE` | django.db.backends.postgresql | указываем, что работаем с postgresql |
| `DB_NAME` | postgres | имя базы данных |
| `POSTGRES_USER` | postgres | логин для подключения к базе данных |
| `POSTGRES_PASSWORD` | postgres | пароль для подключения к БД (установите свой) |
| `DB_HOST` | db | название сервиса (контейнера) |
| `DB_PORT` | 5432 | порт для подключения к БД |
| `DJANGO_SUPERUSER_USERNAME` | admin | логин суперпользователя (установите свой) |
| `DJANGO_SUPERUSER_PASSWORD` | admin | пароль суперпользователя (установите свой) |
| `DJANGO_SUPERUSER_EMAIL` | admin@ya.ru | email суперпользователя (установите свой) |
| `DJANGO_DEBUG` | False | режим отладки |
| `NGINX_DOCKER_PORT` | 80 | проброшенный наружу порт nginx |

## Используемые технологии

```
Python 3.9, Django 3.2.1 (django rest framework + djoser), PostgreSQL, Docker, React
```

## Авторы

[Константин Сидельников](https://github.com/sidelkin1)
