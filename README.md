###Начало работы:

В .env файл вписать название базы данных, юзера, пароль, хост и порт

Поднять базу данных в докере:

>docker-compose up -d

Установить зависимости:

>pip install -r requirements.txt

Сделать миграции:

>pip manage.py migrate

Запустить приложение

>pip manage.py runserver

###URLS:
####1. Регистрация нового пользователя:
>**POST** api/v1/user/register/

JSON-данные для отправки:
```
{
    "email": "vmarket_admin@mail.ru",
    "password": "h6Fv3Sl9Vd",
    "first_name": "Сергей",
    "last_name": "Иванов",
    "middle_name": "Степанович",
    "company": "Video Market",
    "position": "product manager",
    "type": "shop"
}
```

*middle_name*, *company*, *position* - не обязательно

*type* (по умолчанию *buyer*)

В поле *type* указывается *shop* для магазина, *buyer* для покупателей и *admin* для суперпользователя (присваивается автоматически при создании суперпользователя)

####2. Получение токена:
>**POST** api/v1/user/login/

JSON-данные для отправки:
```
{
    "email": "vmarket_admin@mail.ru",
    "password": "h6Fv3Sl9Vd"
}
```
####3. Создание адреса пользователя:
**HEADERS**: Token
>**POST** api/v1/user/contact/

JSON-данные для отправки:
```
{
    "city": "Екатеринбург",
    "street": "Ленина",
    "house": "30",
    "building": "Б",
    "apartment": "101",
    "phone": "9655094301"
}
```
*building* и *apartment* - не обязательно

####4. Просмотр адреса пользователя:
**HEADERS**: Token
>**GET** api/v1/user/contact/

####5. Изменение адреса пользователя:
**HEADERS**: Token
>**PATCH** api/v1/user/contact/

JSON-данные для отправки:

Поля, которые хотим изменить (city, street, house, building, apartment, phone)

####6. Создание магазина:
**HEADERS**: Token

(только для пользователей с type = shop)
>**POST** api/v1/shop/

JSON-данные для отправки:
```
{
    "name": "Digital Shop",
    "url": "http://digitalshop.ru/"
    "state": "true"
}
```
*url* - не обязательно, *state* - по умолчанию True

####7. Просмотр информации о магазине:
**HEADERS**: Token

(только для пользователей с type = shop)
>**GET** api/v1/shop/

####8. Изменение магазина:
**HEADERS**: Token

(только для пользователей с type = shop)
>**PATCH** api/v1/shop/

JSON-данные для отправки:

Поля, которые хотим изменить (name, url, state)

####9. Удаление магазина:
**HEADERS**: Token

(только для пользователей с type = shop)
>**DELETE** api/v1/shop/

####10. Загрузка товаров в магазин:
**HEADERS**: Token

(только для пользователей с type = shop)
>**POST** api/v1/shop/update/

JSON-данные для отправки:

```
{
    "url": "http://....file.yml"
}
```

В **url** должна быть прямая ссылка на файл формата yml
(пример файлов: https://github.com/gchernousov/diplom/tree/dev_api/yaml_files)

####11. Просмотр категорий товаров:
>**GET** api/v1/categories/

####12. Просмотр товаров:
>**GET** api/v1/products/

Возможные параметры для поиска:

* по имени (name)
* по категории (category)
* по стоимости больше, чем Х (price_gte)
* по стоимости меньше, чем Х (price_lte)

```
api/v1/products/?name=galaxy&price_lte=50000
```

####13. Просмотр подробной информации о товаре:
>**GET** api/v1/products/1

####14. Добавление товаров в корзину:
**HEADERS**: Token
>**POST** api/v1/basket/

JSON-данные для отправки:

```
{
    "items": [
        {"product": 3, "quantity": 1},
        {"product": 4, "quantity": 1},
        {"product": 7, "quantity": 1},
        {"product": 8, "quantity": 1}
    ]
}
```
При повторном добавлении товара, который уже есть в корзине, количество суммируется

####15. Просмотр товаров в корзине:
**HEADERS**: Token
>**GET** api/v1/basket/

Так же выводится примерная стоимость будущего заказа

####16. Удаление товаров из корзины:
**HEADERS**: Token
>**DELETE** api/v1/basket/

JSON-данные для отправки:

```
{"products": "2,4,6,7,9"}
```

В *products* в виде строки перечисляются *id* товаров, которые нужно удалить из корзины

####17. Создание заказа (для пользователя):
**HEADERS**: Token
>**POST** api/v1/basket/

JSON-данные не передаются. Все товары, которые находятся у пользователя в корзине, становятся заказом со статусов **new**

####18. Просмотр всех заказо (для пользователя):
**HEADERS**: Tokenв
>**GET** api/v1/basket/

####19. Просмотр всех заказов (для магазина):
**HEADERS**: Token
>**GET** api/v1/shop/orders/

Результат: Все заказы, в которых есть товары магазина с информацией о пользователе, который их заказал

Возможные параметры для поиска:

* по статусу (status)

```
api/v1/shop/orders/?status=new
```
