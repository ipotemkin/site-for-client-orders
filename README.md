# Инфраструктура (Docker Compose)

Изолированный контур для приложения: единственная внешняя точка
входа — **Nginx**. PostgreSQL и Backend недоступны с хоста напрямую.
Образы Backend пушатся в **локальный Docker Registry** с машин
разработчиков (`docker login` + `docker push`).

## Сервисы

| Сервис | Назначение | Внешний доступ |
|--------|------------|----------------|
| **Nginx** | Reverse proxy (Frontend, API, pgAdmin) | Да (`NGINX_HTTP_PORT`, по умолчанию 80) |
| **Postgres** | Серверная БД | Нет (только сеть `internal`) |
| **pgAdmin** | Админ-UI к БД | Только через Nginx: `/pgadmin/` |
| **Registry** | Локальный реестр образов | Да (`REGISTRY_PORT`, по умолчанию 5000) |
| **Watchtower** (`nickfedor/watchtower`) | Автообновление контейнеров при новом образе | Нет |
| **Backend** | API (пока закомментирован в compose) | Нет портов; только через Nginx |

## Сети и безопасность

```
Internet
   │
   ▼
┌─────────────┐     edge network
│    Nginx    │──────────────────────► Registry :5000
│  (ports 80) │
└──────┬──────┘
       │ internal network (internal: true)
       ├──────────► Backend   (без publish ports)
       ├──────────► Postgres  (без publish ports)
       └──────────► pgAdmin   (без publish ports)
```

Требования, которые закрывает эта схема:

1. **Хранилище** — Postgres на той же машине, данные в volume
   `postgres_data`. С хоста порт БД не опубликован.
2. **Доступ к БД** — только с сервисов в сети `internal`
   (Backend, pgAdmin). Клиенты снаружи до Postgres не доходят.
3. **API** — Backend не публикует порты; снаружи возможен только
   путь через Nginx (`/api/` — раскомментировать вместе с Backend).
4. **Изоляция** — сеть `internal` помечена `internal: true`:
   контейнеры в ней не имеют выхода в интернет.
5. **Данные клиентов** — остаются в volume’ах на сервере, наружу
   не реплицируются этой конфигурацией.

## Быстрый старт

```bash
cp .env.example .env
# отредактируйте пароли и REGISTRY_HOST

chmod +x scripts/create-registry-auth.sh
./scripts/create-registry-auth.sh

docker compose up -d
```

Проверка Nginx: `http://<server>/health` → `ok`.

## Docker Registry (push с локальной машины)

### 1. Учётка для `docker login`

Скрипт `scripts/create-registry-auth.sh` создаёт файл
`registry/auth/htpasswd` из `REGISTRY_USER` / `REGISTRY_PASSWORD`
в `.env`. Registry принимает стандартный `docker login`.

После смены пароля пересоздайте htpasswd и перезапустите registry:

```bash
./scripts/create-registry-auth.sh
docker compose up -d registry
```

### 2. Insecure registry (HTTP)

Сейчас Registry слушает HTTP. На машине, с которой пушите образы,
добавьте insecure-registry в Docker Engine, например в
`~/.docker/daemon.json` (Linux) или в Docker Desktop →
Settings → Docker Engine:

```json
{
  "insecure-registries": ["your.server.example.com:5000"]
}
```

Подставьте свой `REGISTRY_HOST` и `REGISTRY_PORT`, затем
перезапустите Docker.

> Для продакшена рекомендуется TLS (сертификат на Nginx или
> Registry) и убрать insecure-registries.

### 3. Login / push / pull

```bash
docker login your.server.example.com:5000
# Username / Password — как в .env (REGISTRY_*)

docker tag my-backend:latest \
  your.server.example.com:5000/backend:latest

docker push your.server.example.com:5000/backend:latest
```

Watchtower периодически проверяет образы контейнеров с label
`com.centurylinklabs.watchtower.enable=true` и при наличии
новой версии пересоздаёт контейнер (в т.ч. Backend, когда он
будет включён).

## pgAdmin: как смотреть БД

1. Откройте в браузере: `http://<server>/pgadmin/`
2. Войдите с `PGADMIN_DEFAULT_EMAIL` и `PGADMIN_DEFAULT_PASSWORD`
   из `.env`.
3. Добавьте сервер (Register → Server):

   | Поле | Значение |
   |------|----------|
   | Name | любое (например `local`) |
   | Host | `postgres` (имя сервиса в Docker) |
   | Port | `5432` |
   | Maintenance database | значение `POSTGRES_DB` |
   | Username | значение `POSTGRES_USER` |
   | Password | значение `POSTGRES_PASSWORD` |

Host именно `postgres`, не `localhost`: pgAdmin ходит в БД
по внутренней Docker-сети.

Прямого URL/порта Postgres на хосте нет — это сделано намеренно.

### Ошибка `no such column: server.tunnel_keep_alive`

Внутренняя SQLite pgAdmin устарела относительно образа
(часто после автообновления). Данные Postgres не затрагиваются —
сбрасывается только UI-конфиг pgAdmin (сохранённые серверы):

```bash
docker compose stop pgadmin
docker compose rm -f pgadmin
docker volume rm "$(docker compose config --volumes \
  | grep pgadmin_data)"
docker compose up -d pgadmin
```

Образ закреплён (`dpage/pgadmin4:8.14`), Watchtower для pgAdmin
выключен, чтобы ошибка не повторялась.

## Backend (когда появится образ)

1. Запушьте образ в Registry (см. выше).
2. В `docker-compose.yml` раскомментируйте сервис `backend`.
3. В `nginx/nginx.conf` раскомментируйте `location /api/`.
4. При необходимости раскомментируйте Frontend `location /`.
5. `docker compose up -d`.

Backend остаётся только в сети `internal`, без `ports:` —
внешний запрос к API в обход Nginx невозможен.

## Полезные команды

```bash
docker compose ps
docker compose logs -f nginx
docker compose logs -f postgres
docker compose down          # остановить, volume’ы сохранить
docker compose down -v       # ВНИМАНИЕ: удалит данные БД
```

## Файлы

```
.
├── docker-compose.yml
├── .env.example
├── nginx/nginx.conf
├── registry/auth/          # htpasswd (не коммитить)
├── scripts/create-registry-auth.sh
└── README.md
```

Секреты храните только в `.env` (файл в `.gitignore`).
