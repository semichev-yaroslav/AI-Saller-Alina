# AI Saller Alina

Production-like backend-проект для портфолио AI Engineer / LLM Engineer.

`AI Saller Alina` автоматически обрабатывает входящие сообщения клиентов (Telegram/API), определяет `intent`, стадию лида, генерирует ответ через LLM и сохраняет полную историю диалога.
Персона бота: Алина, менеджер по продажам по внедрению AI в бизнес-процессы.

## Portfolio focus

Этот репозиторий создан как инженерная демонстрация навыков программирования и AI-разработки:

- проектирование backend-архитектуры (слои API/Service/Repository/Integrations);
- production-like интеграция LLM в бизнес-логику;
- работа с PostgreSQL, миграциями и моделями данных;
- интеграция Telegram Bot API и внешних сервисов;
- тестирование (unit + API), Docker и reproducible local setup.

## Возможности

- Обработка входящих сообщений из Telegram (long polling) и через demo endpoint.
- Сохранение всей переписки в PostgreSQL.
- AI-анализ:
  - intent detection
  - lead stage classification
  - reply generation с учетом истории диалога и каталога услуг
- Строгий контракт AI-ответа: `intent`, `stage`, `reply_text`, `confidence`.
- Seed демо-каталога услуг с ценами `price_from`.
- API для просмотра лидов, сообщений и услуг.
- Логи по входящим сообщениям, AI-вызовам, ошибкам и исходящим ответам.
- Продуктовый оффер: AI-менеджер, который обрабатывает заявки, сохраняет статистику, ведет воронку продаж, прогревает клиента, выводит к продаже, работает с документами/прайсами и интегрируется с CRM.

## Технологии

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- OpenAI API
- Telegram Bot API
- Docker / Docker Compose
- pytest

## Архитектура

Слои:

- `API` — HTTP endpoints.
- `Services` — orchestration бизнес-логики.
- `Repositories` — доступ к данным (SQLAlchemy queries).
- `AI module` — построение prompt, вызов OpenAI, валидация результата.
- `Integrations` — Telegram API client.
- `Workers` — long polling loop для Telegram.

### Поток обработки

1. Пользователь отправляет сообщение в Telegram.
2. Worker получает update.
3. Входящее сообщение сохраняется в `messages`.
4. AI получает контекст (история + каталог услуг), возвращает structured response.
5. Результат AI сохраняется в `ai_runs`.
6. Ответ сохраняется в `messages` и отправляется в Telegram.
7. Стадия и intent лида обновляются в `leads`.

## Стартовое сообщение для нового лида

Для нового Telegram-пользователя система автоматически добавляет onboarding-вступление:

- представляется как Алина, менеджер по продажам AI-решений,
- кратко перечисляет доступные услуги,
- задает вопрос для выявления потребностей клиента.

Это сообщение добавляется к первому AI-ответу.

## Структура проекта

```text
ai-sales-manager/
  app/
    api/
    ai/
    core/
    db/
    integrations/
    repositories/
    schemas/
    services/
    workers/
  alembic/
    versions/
  tests/
  Dockerfile
  docker-compose.yml
  .env.example
  alembic.ini
  pyproject.toml
```

## Модель данных

### `leads`

- Telegram-идентификаторы пользователя/чата
- профиль лида (`username`, `full_name`, `phone`, `email`)
- текущая стадия (`new`, `engaged`, `qualified`, `interested`, `booking_pending`, `booked`, `lost`)
- последний intent

### `messages`

- входящие/исходящие сообщения
- source (`user`, `assistant`, `system`)
- channel (`telegram`, `api_simulation`)
- delivery status (`pending`, `sent`, `failed`)
- Telegram metadata (`telegram_message_id`, `telegram_update_id`)

### `services`

- каталог услуг
- описание
- `price_from`, `currency`

### `ai_runs`

- лог AI вызова
- определенный intent/stage/confidence
- текст ответа
- raw response
- статус (`success`, `error`)

## Intent и Lead Stages

### Intent

- `greeting`
- `service_question`
- `price_question`
- `objection`
- `ready_to_buy`
- `booking_intent`
- `contact_sharing`
- `unclear`

### Lead stages

- `new`
- `engaged`
- `qualified`
- `interested`
- `booking_pending`
- `booked`
- `lost`

## API

### Обязательные endpoints

- `GET /health`
- `GET /leads`
- `GET /leads/{id}`
- `GET /leads/{id}/messages`
- `POST /simulate/message`
- `GET /services`

### Примеры

```bash
curl http://localhost:8000/health
```

```bash
curl "http://localhost:8000/leads?stage=interested&search=ivan"
```

```bash
curl -X POST http://localhost:8000/simulate/message \
  -H 'Content-Type: application/json' \
  -d '{
    "telegram_user_id": 12345,
    "telegram_chat_id": 12345,
    "username": "ivan",
    "full_name": "Ivan Petrov",
    "text": "Здравствуйте, хочу узнать цену AI-бота"
  }'
```

## Конфигурация

Скопируйте `.env.example` в `.env` и заполните секреты:

- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `DATABASE_URL`

## Запуск через Docker

```bash
cp .env.example .env
# заполните OPENAI_API_KEY и TELEGRAM_BOT_TOKEN

docker compose up --build
```

После старта:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Локальный запуск без Docker

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env

alembic upgrade head
uvicorn app.main:app --reload
```

Telegram worker в отдельном процессе:

```bash
python -m app.workers.telegram_polling
```

## Тесты

```bash
pytest
```

Покрыто:

- unit tests (AI logic + message processor)
- API tests (`/simulate/message`, `/leads`, `/leads/{id}`, `/leads/{id}/messages`)

## Engineering notes

- Идемпотентность Telegram update: уникальный индекс на `telegram_update_id`.
- Контакты (phone/email) извлекаются из текста и сохраняются в `leads`.
- При низкой уверенности и сложных возражениях бот предлагает подключение менеджера.
- Если `OPENAI_API_KEY` не задан, используется fallback heuristic analyzer для локального демо.
