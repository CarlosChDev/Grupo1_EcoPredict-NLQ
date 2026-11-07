#!/usr/bin/env bash
# Portable, encrypted EcoPredict backup. Intended for the Docker host only.
set -Eeuo pipefail
umask 077

usage() { echo "Usage: $0 --key-file FILE [--output-dir DIR] [--backup-id ID] [--compose-file FILE] [--env-file FILE]" >&2; }
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/infrastructure/docker-compose.yml"; ENV_FILE="$ROOT_DIR/infrastructure/.env"
OUT_DIR="$ROOT_DIR/backups"; BACKUP_ID="ecopredict-$(date -u +%Y%m%dT%H%M%SZ)"; KEY_FILE=""
PG_CONTAINER="${PG_CONTAINER:-aire_postgres}"; N8N_VOLUME="${N8N_VOLUME:-aire_n8n_data}"; PROJECT_NAME="${COMPOSE_PROJECT_NAME:-calidad-aire}"
while (($#)); do case "$1" in
  --key-file) KEY_FILE="$2"; shift 2;; --output-dir) OUT_DIR="$2"; shift 2;; --backup-id) BACKUP_ID="$2"; shift 2;;
  --compose-file) COMPOSE_FILE="$2"; shift 2;; --env-file) ENV_FILE="$2"; shift 2;; -h|--help) usage; exit 0;; *) usage; exit 2;; esac; done
[[ -n "$KEY_FILE" && -r "$KEY_FILE" && -r "$ENV_FILE" && -f "$COMPOSE_FILE" ]] || { echo "Missing key, Compose file or protected env file." >&2; exit 2; }
[[ "$BACKUP_ID" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "Invalid backup id." >&2; exit 2; }
for command in docker gpg sha256sum tar awk; do command -v "$command" >/dev/null || { echo "Required command unavailable: $command" >&2; exit 127; }; done

# Do not source .env: it can contain shell-significant values. POSTGRES_USER is an identifier, not a secret.
PG_ADMIN="${PG_BACKUP_ADMIN:-$(awk -F= '$1 == "POSTGRES_USER" {sub(/^[^=]*=/, ""); print; exit}' "$ENV_FILE")}"
[[ "$PG_ADMIN" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || { echo "A valid POSTGRES_USER or PG_BACKUP_ADMIN is required." >&2; exit 2; }
docker inspect "$PG_CONTAINER" >/dev/null; docker volume inspect "$N8N_VOLUME" >/dev/null
docker compose -p "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config -q
docker exec "$PG_CONTAINER" psql -U "$PG_ADMIN" -d postgres -Atqc 'SELECT rolsuper FROM pg_roles WHERE rolname = current_user' | grep -qx t || {
  echo "The PostgreSQL backup account must be a superuser to capture global roles." >&2; exit 1; }
mkdir -p "$OUT_DIR"; OUT_DIR="$(cd "$OUT_DIR" && pwd)"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/ecopredict-backup.XXXXXX")"; PAYLOAD="$WORK/payload"; mkdir -p "$PAYLOAD/postgres"
N8N_STOPPED=0
cleanup() { local rc=$?; if ((N8N_STOPPED)); then docker compose -p "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" start n8n >/dev/null 2>&1 || true; fi; rm -rf "$WORK"; exit "$rc"; }
trap cleanup EXIT

# n8n is paused only while the database and its persistent volume are captured.
docker compose -p "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" stop n8n >/dev/null; N8N_STOPPED=1
docker exec "$PG_CONTAINER" pg_dump -U "$PG_ADMIN" -Fc -d n8n > "$PAYLOAD/postgres/n8n.dump"
docker exec "$PG_CONTAINER" pg_dump -U "$PG_ADMIN" -Fc -d calidad_aire > "$PAYLOAD/postgres/calidad_aire.dump"
docker exec "$PG_CONTAINER" pg_dumpall -U "$PG_ADMIN" --globals-only --no-role-passwords > "$PAYLOAD/postgres/globals.sql"
docker exec "$PG_CONTAINER" psql -U "$PG_ADMIN" -d postgres -Atqc "SELECT rolname FROM pg_roles ORDER BY rolname" > "$PAYLOAD/postgres/roles.txt"
for file in "$PAYLOAD/postgres/n8n.dump" "$PAYLOAD/postgres/calidad_aire.dump" "$PAYLOAD/postgres/globals.sql" "$PAYLOAD/postgres/roles.txt"; do [[ -s "$file" ]] || { echo "A PostgreSQL backup component is empty." >&2; exit 1; }; done
docker exec -i "$PG_CONTAINER" pg_restore -l < "$PAYLOAD/postgres/n8n.dump" >/dev/null
docker exec -i "$PG_CONTAINER" pg_restore -l < "$PAYLOAD/postgres/calidad_aire.dump" >/dev/null
docker image inspect alpine:3.20 >/dev/null || { echo "Required local helper image alpine:3.20 is unavailable." >&2; exit 1; }
docker run --pull=never --rm -v "$N8N_VOLUME:/source:ro" alpine:3.20 sh -c 'tar -C /source -czf - --numeric-owner .' > "$PAYLOAD/n8n-volume.tar.gz"
tar -tzf "$PAYLOAD/n8n-volume.tar.gz" >/dev/null
cp "$ENV_FILE" "$PAYLOAD/runtime.env"; cp "$COMPOSE_FILE" "$PAYLOAD/docker-compose.yml"
[[ -d "$ROOT_DIR/infrastructure/nginx" ]] && cp -a "$ROOT_DIR/infrastructure/nginx" "$PAYLOAD/nginx"
printf 'format=ecopredict-backup-v2\ncreated_utc=%s\npostgres_container=%s\nn8n_volume=%s\n' "$(date -u +%FT%TZ)" "$PG_CONTAINER" "$N8N_VOLUME" > "$PAYLOAD/manifest.txt"
tar -C "$PAYLOAD" -czf "$WORK/$BACKUP_ID.tar.gz" .
# GnuPG's symmetric AES-256 envelope authenticates encrypted data during decrypt; the passphrase can be any GitHub Secret value.
gpg --batch --yes --pinentry-mode loopback --passphrase-file "$KEY_FILE" --symmetric --cipher-algo AES256 --s2k-mode 3 --s2k-digest-algo SHA512 --output "$OUT_DIR/$BACKUP_ID.tar.gz.gpg" "$WORK/$BACKUP_ID.tar.gz"
(cd "$OUT_DIR" && sha256sum "$BACKUP_ID.tar.gz.gpg" > "$BACKUP_ID.tar.gz.gpg.sha256")
gpg --batch --quiet --pinentry-mode loopback --passphrase-file "$KEY_FILE" --decrypt "$OUT_DIR/$BACKUP_ID.tar.gz.gpg" | tar -tzf - >/dev/null
echo "Encrypted backup created: $BACKUP_ID.tar.gz.gpg"
