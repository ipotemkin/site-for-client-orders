# Autello — заявки на премиальный тюнинг

Веб-контур ателье дооснащения автомобилей: клиент оставляет
заявку на услугу (Bose, покраска, аэрография и т.п.), админ
управляет каталогом услуг и смотрит заявки. Данные хранятся
в Postgres на той же машине; снаружи доступен только Nginx.

## Суть продукта

| Страница | URL | Назначение |
|----------|-----|------------|
| Лендинг + заявка | `/` | Выбор услуги, контакты, авто, бюджет, способ связи |
| Админка | `/admin` | CRUD услуг, диапазон бюджета на форме, список заявок |
| API / Swagger | `/api/docs` | FastAPI |
| pgAdmin | `/pgadmin/` | Просмотр БД |

Фронтенд (React + TypeScript) собирает заявку и поведение
пользователя на странице, отправляет пакет в backend.
Backend пишет в Postgres. Авторизация админки — позже.

### Данные

- **services** — каталог услуг (название, описание, цена от,
  срок, порядок, активность)
- **leads** — заявки клиентов
- **lead_behaviors** — метрики поведения (1:1 с заявкой)
- **admin_settings** — общий min/max бюджета на ползунке формы

## Состав стека

```
Internet
   │
   ▼
┌─────────────┐     edge
│    Nginx    │──────────────────► Registry :5000
│   (port 80) │
└──────┬──────┘
       │ internal (internal: true)
       ├──────────► Frontend   (React SPA)
       ├──────────► Backend    (FastAPI)
       ├──────────► Postgres
       └──────────► pgAdmin
```

| Сервис | Роль | Снаружи |
|--------|------|---------|
| **Nginx** | Reverse proxy | Да (`NGINX_HTTP_PORT`, по умолчанию 80) |
| **Frontend** | React + TS (Vite) | Только через `/` |
| **Backend** | FastAPI + asyncpg | Только через `/api/` |
| **Postgres** | БД заявок и услуг | Нет |
| **pgAdmin** | UI к БД | Только `/pgadmin/` |
| **Registry** | Локальный реестр образов | Да (`REGISTRY_PORT`) |
| **Watchtower** | Автообновление образов по label | Нет |

Frontend и Backend сейчас собираются из локального контекста
(`build: ./frontend`, `build: ./backend`). Образы из Registry
можно вернуть позже (закомментированные `image:` в compose).

## Структура репозитория

```
.
├── backend/                 # FastAPI
│   ├── main.py
│   ├── core/                # пул Postgres (asyncpg)
│   ├── models/              # Lead, Behavior, Service, Admin + CRUD
│   └── routes/
├── frontend/                # React + TypeScript (Vite)
│   └── src/
│       ├── pages/           # HomePage, AdminPage
│       ├── components/
│       └── api/
├── nginx/nginx.conf
├── pgadmin/entrypoint.sh    # авто-регистрация сервера Postgres
├── registry/auth/           # htpasswd (не коммитить)
├── scripts/create-registry-auth.sh
├── docker-compose.yml
├── .env.example
└── README.md
```

## Запуск

### 1. Окружение

```bash
cp .env.example .env
# задайте POSTGRES_*, PGADMIN_*, REGISTRY_*
```

### 2. Auth для Registry (если нужен push/pull)

```bash
chmod +x scripts/create-registry-auth.sh
./scripts/create-registry-auth.sh
```

### 3. Поднять стек

```bash
docker compose up -d --build
```

Первый запуск соберёт образы `backend:local` и `frontend:local`.

### 4. Проверка

| URL | Ожидание |
|-----|----------|
| `http://<host>/health` | `ok` |
| `http://<host>/` | лендинг Autello |
| `http://<host>/admin` | админка |
| `http://<host>/api/docs` | Swagger |
| `http://<host>/api/health` | `{"status":"ok"}` |
| `http://<host>/pgadmin/` | вход по `PGADMIN_*` из `.env` |

### Полезные команды

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose up -d --build backend frontend   # пересборка приложений
docker compose down                             # стоп, volume’ы сохранить
docker compose down -v                          # ВНИМАНИЕ: удалит данные БД
```

## Безопасность контура

1. Postgres без publish ports — только сеть `internal`.
2. Backend и Frontend без publish ports — только через Nginx.
3. Сеть `internal` с `internal: true` — без выхода в интернет.
4. Секреты только в `.env` (в `.gitignore`).

## pgAdmin

Сервер **Postgres** регистрируется при старте контейнера
(`pgadmin/entrypoint.sh` + `POSTGRES_*` из `.env`).

1. `http://<host>/pgadmin/`
2. Логин: `PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD`
3. **Servers → Postgres → Databases → `<POSTGRES_DB>`**

Host в подключении — `postgres` (имя сервиса Docker), не
`localhost`.

### Ошибка `no such column: server.tunnel_keep_alive`

Сброс только UI-конфига pgAdmin (данные Postgres не трогаются):

```bash
docker compose stop pgadmin
docker compose rm -f pgadmin
docker volume rm "$(docker compose config --volumes \
  | grep pgadmin_data)"
docker compose up -d pgadmin
```

Образ закреплён: `dpage/pgadmin4:8.14`, Watchtower для pgAdmin
выключен.

## Docker Registry (опционально)

Для push с машин разработчиков:

1. `./scripts/create-registry-auth.sh`
2. Insecure registry в Docker Engine:
   `["<REGISTRY_HOST>:<REGISTRY_PORT>"]`
3. `docker login <REGISTRY_HOST>:<REGISTRY_PORT>`
4. `docker tag … && docker push …`

Watchtower обновляет контейнеры с label
`com.centurylinklabs.watchtower.enable=true`. Для локальной
сборки backend/frontend label выключен.
