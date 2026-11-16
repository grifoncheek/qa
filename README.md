# QA-портфолио: тестирование UI, REST API и SQL

Учебный проект, в котором я показываю полный цикл работы с качеством: анализ стенда, тест-дизайн, проверку UI и серверной логики, оформление тест-кейсов и баг-репортов, SQL и стартовую автоматизацию API.

## Объекты тестирования

Я работаю с тремя объектами. [Swag Labs](https://www.saucedemo.com) — демо-магазин: проверяю авторизацию, каталог, сортировку, корзину и оформление заказа. [Restful-Booker](https://restful-booker.herokuapp.com) — демо-API бронирования: аутентификация, CRUD, фильтры, валидация и коды ответов. Учебная БД «Банк» — схема clients / accounts / cards / transactions и 20 SQL-запросов. Все стенды публичные и предназначены для обучения тестированию.

## Что проверял и что получилось

Я проверил функциональные, негативные, регрессионные, smoke-, интеграционные (API) и исследовательские сценарии; виды тестирования и подход описаны в docs/test-plan.md. Составил 36 тест-кейсов (16 UI, 20 API; 22 позитивных и 14 негативных) в формате CSV для Test IT — docs/test-cases.csv и читаемая версия docs/test-cases.md. Нашёл и оформил 14 дефектов с указанием severity/priority и статусами жизненного цикла — docs/bug-reports.md. Подготовил Postman-коллекцию из 15 запросов с 28 проверками — postman/. Написал 27 pytest-тестов для API: 16 проходят, 11 помечены xfail со ссылками на известные баги — tests/. Выполнил 20 SQL-задач на схеме из 4 таблиц (15 клиентов, 22 счёта, 18 карт, 60 транзакций) с автопроверкой результата — sql/.

## Структура проекта

    .
    ├── docs/
    │   ├── test-plan.md          тест-план и стратегия
    │   ├── checklist.md          чек-листы UI, API, SQL
    │   ├── test-design.md        техники тест-дизайна с примерами
    │   ├── test-cases.csv        тест-кейсы для импорта в Test IT
    │   ├── test-cases.md         читаемая версия (генерируется из CSV)
    │   ├── bug-reports.md        14 воспроизведённых дефектов
    │   └── resume.md             формулировки для резюме
    ├── postman/
    │   ├── restful-booker.postman_collection.json
    │   └── restful-booker.postman_environment.json
    ├── sql/
    │   ├── schema.sql            схема БД «Банк»
    │   ├── seed.sql              тестовые данные
    │   └── queries.sql           20 запросов с ожидаемыми результатами
    ├── tests/                    pytest-тесты API
    ├── scripts/
    │   ├── build_test_cases_md.py
    │   └── check_sql.py
    ├── .github/workflows/qa.yml  CI: артефакты, SQL, pytest, newman
    └── pytest.ini

## Как запустить

    # API-автотесты
    pip install -r tests/requirements.txt
    pytest

    # Postman-коллекция
    npm install -g newman
    newman run postman/restful-booker.postman_collection.json \
      -e postman/restful-booker.postman_environment.json --timeout-request 15000

    # SQL-запросы
    python3 scripts/check_sql.py

    # Пересборка документов из CSV
    python3 scripts/build_test_cases_md.py

Тест-кейсы можно импортировать в Test IT из docs/test-cases.csv (UTF-8, разделитель ;, шаги разделены символом |).

## Статус проверок

Все дефекты API воспроизведены вручную и продублированы автотестами; прогоны newman и pytest выполняются командами выше и завершаются без падений. Для UI я подготовил чек-лист и 16 тест-кейсов под ручной прогон — я оставил его ручным, потому что здесь я тренирую ручные техники. Все 20 SQL-запросов и операции DML проверяет скрипт scripts/check_sql.py на SQLite.

## Ограничения

Публичные стенды могут быть недоступны или менять данные, поэтому тесты создают и удаляют свои записи, а в дефектах указаны команды воспроизведения. Синтаксис, специфичный для MySQL/PostgreSQL, вынесен в комментарии к запросам. Нагрузочное и security-тестирование в scope не входит.
