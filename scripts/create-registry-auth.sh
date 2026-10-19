#!/usr/bin/env sh
# Generate htpasswd for the local Docker Registry.
# Usage:
#   ./scripts/create-registry-auth.sh
# or:
#   REGISTRY_USER=deploy REGISTRY_PASSWORD=secret \
#     ./scripts/create-registry-auth.sh

set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
AUTH_DIR="${ROOT_DIR}/registry/auth"
HTPASSWD_FILE="${AUTH_DIR}/htpasswd"

if [ -f "${ROOT_DIR}/.env" ]; then
  # shellcheck disable=SC1091
  set -a
  . "${ROOT_DIR}/.env"
  set +a
fi

USER_NAME="${REGISTRY_USER:-}"
USER_PASS="${REGISTRY_PASSWORD:-}"

if [ -z "${USER_NAME}" ] || [ -z "${USER_PASS}" ]; then
  echo "Set REGISTRY_USER and REGISTRY_PASSWORD in .env" >&2
  echo "or export them before running this script." >&2
  exit 1
fi

mkdir -p "${AUTH_DIR}"

docker run --rm --entrypoint htpasswd \
  httpd:2 \
  -Bbn "${USER_NAME}" "${USER_PASS}" > "${HTPASSWD_FILE}"

chmod 600 "${HTPASSWD_FILE}"
echo "Created ${HTPASSWD_FILE}"
echo "Login from a client machine:"
echo "  docker login <REGISTRY_HOST>:<REGISTRY_PORT>"
