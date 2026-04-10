# api_yamdb
 
API для проекта YaMDB. Реализованы модели, сериализаторы, представления для работы с пользователями, произведениями, категориями, жанрами, отзывами на произведения, комментариев. Настроена маршрутизация, двухэтапная регистрация пользователей с отправкой индивидуального кода подтверждения на почту, аутентификация через JWT, права доступа для различных категорий пользователей.
 
## Технологии 
- Python 3.12.7 
- Django 
- django-filter
- djangorestframework 
- djangorestframework_simplejwt
- pytest 
 
## Запуск проекта 
1. Клонируйте репозиторий и перейдите в него 
 
2. Создайте и активируйте виртуальное окружение: 
 
``` 
python -m venv venv 
``` 
 
``` 
source venv/Scripts/activate 
``` 
 
3. Установите зависимости из файла requirements.txt: 
 
``` 
python -m pip install --upgrade pip 
``` 
 
``` 
pip install -r requirements.txt 
``` 
 
4. Выполните миграции: 
 
``` 
python manage.py migrate 
``` 
 
5. Запустите проект: 
 
``` 
python manage.py runserver 
``` 
 
## Примеры запросов к API 
- `POST /api/v1/auth/signup/` — Регистрация нового пользователя и плучение кода подтверждения на переданный email. 
- `POST /api/v1/auth/token/` — Получение JWT-токена в обмен на username и confirmation code. 
- `GET /api/v1/categories/` — Получить список всех категорий.
- `DELETE /api/v1/categories/{slug}/` — Удалить категорию. 
- `GET /api/v1/genres/` — Получить список всех жанров. 
- `POST /api/v1/genres/` — Добавить жанр. 
- `GET /api/v1/titles/{titles_id}/` — Информация о произведении. 
- `PATCH /api/v1/titles/{titles_id}/` — Обновить информацию о произведении. 
- `GET /api/v1/titles/{title_id}/reviews/` — Получить список всех отзывов. 
- `POST /api/v1/titles/{title_id}/reviews/` — Добавить новый отзыв. 
- `DELETE /api/v1/titles/{title_id}/reviews/{review_id}/` — Удалить отзыв по id.
- `GET /api/v1/titles/{title_id}/reviews/{review_id}/comments/` — Получить список всех комментариев к отзыву по id
- `PATCH /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` — Частично обновить комментарий к отзыву по id. 
- `GET /api/v1/users/` — Получить список всех пользователей.
- `POST /api/v1/users/` — Добавить нового пользователя.
- `PATCH /api/v1/users/{username}/` — Изменить данные пользователя по username.
- `GET /api/v1/users/me/` — Получить данные своей учетной записи.
 
## Спецификация  
Спецификация доступна в YAML‑файле api_yamdb/static/redoc.yaml, а также через веб‑интерфейс.  
Когда вы запустите проект, по адресу  http://127.0.0.1:8000/redoc/ будет доступна документация для API YaMDB в формате Redoc. 
 
## Авторы проекта 
Проект разработан - [DariaKolesnik27](https://github.com/DariaKolesnik27), [petroocho](https://github.com/petroocho)

