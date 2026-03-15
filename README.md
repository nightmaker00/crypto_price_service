# Crypto Price Service

Сервис:
- раз в минуту запрашивает индексные цены `btc_usd` и `eth_usd` с Deribit;
- сохраняет `ticker`, `price`, `timestamp` (UNIX, seconds) в PostgreSQL;
- предоставляет внешнее API на FastAPI для чтения сохраненных данных.

## Что реализовано по ТЗ

### Обязательные требования
- Клиент Deribit.
- Периодический сбор цен через `Celery Beat` (каждую минуту).
- Хранение данных в `PostgreSQL`.
- Версионные миграции схемы БД через `Alembic`.
- Внешнее API на `FastAPI` с GET-методами и обязательным query-параметром `ticker`:
  - `GET /prices/all?ticker=...` - все сохраненные данные по валюте;
  - `GET /prices/latest?ticker=...` - последняя цена;
  - `GET /prices/by-date?ticker=...&start_timestamp=...&end_timestamp=...` - цены за период.

### Необязательные требования, также выполнил
- Unit tests для основных методов.
- Docker-разворачивание в двух контейнерах, с Celery вынесен в profile.
- `aiohttp` применен в клиенте Deribit.

## Clean Architecture

Структура слоев:
- `app/domain` - сущности и абстракции репозиториев/клиента.
- `app/application` - use-case сервис `PriceService`.
- `app/infrastructure` - адаптеры к PostgreSQL (SQLAlchemy) и Deribit (aiohttp).
- `app/interfaces` - FastAPI роуты и Celery задачи.
- `app/config` - настройки и DI.

## Deribit API

Используется публичный endpoint:
- `GET /public/get_index_price` с query-параметром `index_name`.

Ключевые факты из документации:
- для public market-data методов авторизация не обязательна;
- для задачи подходят значения `index_name=btc_usd` и `index_name=eth_usd`;
- цена приходит в `result.index_price`.

Ссылки на методы из документации:
- [Deribit API index price](https://docs.deribit.com/api-reference/market-data/public-get_index_price)
- [Deribit Authentication](https://docs.deribit.com/articles/authentication)
- [Deribit Rate Limits](https://docs.deribit.com/articles/rate-limits)

## Локальный запуск

### 1) Установка зависимостей
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Настройки окружения
```
cp .env.example .env
```

### 3) Запуск инфраструктуры (PostgreSQL + Redis)
```
docker compose -f deployments/docker-compose.yml up -d postgres redis
```

### 4) Применение миграций
```
alembic upgrade head
```

### 5) Запуск API
```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6) Запуск Celery worker
```
celery -A app.interfaces.celery.celery_app:celery_app worker --loglevel=info
```

### 7) Запуск Celery beat
```
celery -A app.interfaces.celery.celery_app:celery_app beat --loglevel=info
```

## Запуск в Docker

### Базовый режим (только 2 контейнера: `api + postgres`)

```
docker compose -f deployments/docker-compose.yml up --build
```

Сервисы:
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5433`

### Отдельная секция Celery (profile `celery`)

Запуск с Celery (`worker + beat + redis`) поверх базовых контейнеров:

```
docker compose -f deployments/docker-compose.yml --profile celery up --build
```

## Тесты

```
pytest -q
```

## Миграции

- Создать новую миграцию:  
  `alembic revision --autogenerate -m "your_message"`
- Применить миграции:  
  `alembic upgrade head`
- Откатить последнюю миграцию:  
  `alembic downgrade -1`

## Примеры API-запросов

```
curl "http://localhost:8000/prices/all?ticker=btc_usd"
curl "http://localhost:8000/prices/latest?ticker=eth_usd"
curl "http://localhost:8000/prices/by-date?ticker=btc_usd&start_timestamp=1710000000&end_timestamp=1710003600"
```

## Design decisions

1. **UNIX timestamp (seconds) как основной формат времени**  
   Соответствует ТЗ и упрощает фильтрацию/сравнение в БД и API.

2. **Асинхронный стек для I/O** (`aiohttp`, `SQLAlchemy async`)  
   Запросы к внешнему API и БД неблокирующие, что делает сервис более устойчивым под нагрузкой.

3. **Celery task как тонкая оболочка вокруг application service**  
   Бизнес-логика не дублируется. API и фоновые задачи используют один `PriceService`.

4. **Явные абстракции в domain слое**  
   Упрощают тестирование.

5. **Читаемая реализация**  
   Фокус на понятном коде и нейминге.
