#!/bin/sh
# Generate servers.json + pgpass from env, import into pgAdmin,
# then start the official entrypoint.
set -eu

POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:?POSTGRES_USER is required}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
POSTGRES_DB="${POSTGRES_DB:?POSTGRES_DB is required}"
PGADMIN_EMAIL="${PGADMIN_DEFAULT_EMAIL:?PGADMIN_DEFAULT_EMAIL is required}"

# pgAdmin resolves PassFile relative to the user storage dir:
#   /var/lib/pgadmin/storage/<email_with_@->_>/
USER_DIR="$(echo "${PGADMIN_EMAIL}" | sed 's/@/_/g')"
USER_STORAGE="/var/lib/pgadmin/storage/${USER_DIR}"
# Filename only — NOT an absolute path (pgAdmin quirk).
PASSFILE_NAME="pgpass"
USER_PGPASS="${USER_STORAGE}/${PASSFILE_NAME}"

SERVERS_FILE="/tmp/servers.json"
PGPASS_SRC="/tmp/pgpass"

umask 077
printf '%s:%s:*:%s:%s\n' \
  "${POSTGRES_HOST}" \
  "${POSTGRES_PORT}" \
  "${POSTGRES_USER}" \
  "${POSTGRES_PASSWORD}" > "${PGPASS_SRC}"
chmod 600 "${PGPASS_SRC}"

mkdir -p "${USER_STORAGE}"
cp "${PGPASS_SRC}" "${USER_PGPASS}"
chmod 600 "${USER_PGPASS}"

cat > "${SERVERS_FILE}" <<EOF
{
  "Servers": {
    "1": {
      "Name": "Postgres",
      "Group": "Servers",
      "Host": "${POSTGRES_HOST}",
      "Port": ${POSTGRES_PORT},
      "MaintenanceDB": "${POSTGRES_DB}",
      "Username": "${POSTGRES_USER}",
      "PassFile": "${PASSFILE_NAME}",
      "SSLMode": "prefer",
      "Favorite": true
    }
  }
}
EOF

# Official entrypoint also copies this into user storage.
export PGPASS_FILE="${PGPASS_SRC}"
export PGADMIN_SERVER_JSON_FILE="${SERVERS_FILE}"

# Official entrypoint imports servers only when pgadmin4.db is
# missing. Re-import on every start when the DB already exists.
if [ -f /var/lib/pgadmin/pgadmin4.db ]; then
  /venv/bin/python3 /pgadmin4/setup.py load-servers \
    "${SERVERS_FILE}" \
    --user "${PGADMIN_EMAIL}" \
    --replace
fi

exec /entrypoint.sh "$@"
