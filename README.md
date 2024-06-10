# Социальная сеть для публикации постов

## Описание
Проект Blogicum - социальная сеть для публикации постов с возможностью оставлять комментарии к чужим постам.

## Технологии:

- Python 3.9
- Django 3.2
- SQLite3

## Установка (MacOS):

1. Клонирование репозитория

```
git clone https://github.com/veronikabarhatova/django_sprint4.git
```

2. Переход в директорию django_sprint4

```
cd django_sprint4
```

3. Создание виртуального окружения

```
python3 -m venv venv
```

4. Активация виртуального окружения

```
source venv/bin/activate
```

5. Обновите pip

```
python3 -m pip install --upgrade pip
```

6. Установка зависимостей

```
pip install -r requirements.txt
```

7. Применение миграций

```
python3 manage.py migrate
```

8. Загрузить фикстуры в БД

```
python manage.py loaddata db.json
```

9. Создать суперпользователя

```
python manage.py createsuperuser
```

10. Запуск проекта, введите команду

```
python manage.py runserver
```

11. Деактивация виртуального окружения

```
deactivate
```
