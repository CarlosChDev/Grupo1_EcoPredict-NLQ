#!/usr/bin/env bash
# Controlled restore. It creates and validates a persistent rollback backup before mutation.
set -Eeuo pipefail
umask 077

usage() { echo "Usage: $0 --backup-file FILE --key-file FILE --confirm RESTORE [--compose-file FILE] [--env-file FILE]" >&2; }
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/infrastructure/docker-compose.yml"; ENV_FILE="$ROOT_DIR/infrastructure/.env"; BACKUP=""; KEY_FILE=""; CONFIRM=""
PG_CONTAINER="${PG_CONTAINER:-aire_postgres}"; N8N_CONTAINER="${N8N_CONTAINER:-aire_n8n}"; NGINX_CONTAINER="${NGINX_CONTAINER:-aire_nginx}"; N8N_VOLUME="${N8N_VOLUME:-aire_n8n_data}"; PROJECT_NAME="${COMPOSE_PROJECT_NAME:-calidad-aire}"
while (($#)); do case "$1" in
  --backup-file) BACKUP="$2"; shift 2;; --key-file) KEY_FILE="$2"; shift 2;; --confirm) CONFIRM="$2"; shift 2;;
  --compose-file) COMPOSE_FILE="$2"; shift 2;; --env-file) ENV_FILE="$2"; shift 2;; -h|--help) usage; exit 0;; *) usage; exit 2;; esac; done
[[ "$CONFIRM" == RESTORE && -r "$BACKUP" && -r "$KEY_FILE" && -r "$ENV_FILE" && -f "$COMPOSE_FILE" ]] || { echo "Explicit --confirm RESTORE and readable files are required." >&2; exit 2; }
[[ "$(basename "$BACKUP")" =~ ^ecopredict-[A-Za-z0-9._-]+\.tar\.gz\.gpg$ ]] || { echo "Unexpected backup name." >&2; exit 2; }
for command in docker gpg sha256sum tar awk sed curl cmp; do command -v "$command" >/dev/null || { echo "Required command unavailable: $command" >&2; exit 127; }; done
PG_ADMIN="${PG_BACKUP_ADMIN:-$(awk -F= '$1 == "POSTGRES_USER" {sub(/^[^=]*=/, ""); print; exit}' "$ENV_FILE")}"; [[ "$PG_ADMIN" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || { echo "A valid PostgreSQL administrator is required." >&2; exit 2; }
SUM="$BACKUP.sha256"; [[ -r "$SUM" ]] || { echo "Missing SHA-256 sidecar." >&2; exit 2; }; (cd "$(dirname "$BACKUP")" && sha256sum -c "$(basename "$SUM")")
WORK="$(mktemp -d "${TMPDIR:-/tmp}/ecopredict-restore.XXXXXX")"; INCOMING="$WORK/incoming"; ROLLBACK="$WORK/rollback"; mkdir -p "$INCOMING" "$ROLLBACK"
MUTATED=0; ROLLBACK_READY=0; ROLLBACK_RUNNING=0; MODIFIED="none"

restore_payload() {
  local payload="$1"; local label="$2"
  docker compose -p "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" stop n8n
  docker exec "$PG_CONTAINER" psql -U "$PG_ADMIN" -d postgres -v ON_ERROR_STOP=1 -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname IN ('n8n','calidad_aire') AND pid <> pg_backend_pid();"
  for db in n8n calidad_aire; do docker exec "$PG_CONTAINER" psql -U "$PG_ADMIN" -d postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS \"$db\";"; docker exec "$PG_CONTAINER" createdb -U "$PG_ADMIN" "$db"; done
  docker exec -i "$PG_CONTAINER" pg_restore -U "$PG_ADMIN" --exit-on-error -d n8n < "$payload/postgres/n8n.dump"
  docker exec -i "$PG_CONTAINER" pg_restore -U "$PG_ADMIN" --exit-on-error -d calidad_aire < "$payload/postgres/calidad_aire.dump"
  docker run --pull=never --rm -v "$N8N_VOLUME:/target" alpine:3.20 sh -c 'find /target -mindepth 1 -maxdepth 1 -exec rm -rf {} +'
  docker run --pull=never --rm -i -v "$N8N_VOLUME:/target" alpine:3.20 sh -c 'tar -C /target -xzf - --numeric-owner' < "$payload/n8n-volume.tar.gz"
  docker compose -p "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --no-build --pull never postgres n8n aire_nginx
  MODIFIED="$label"
}

health_checks() {
  local i
  for i in {1..30}; do [[ "$(docker inspect -f '{{.State.Health.Status}}' "$PG_CONTAINER")" == healthy ]] && break; sleep 2; done
  [[ "$(docker inspect -f '{{.State.Health.Status}}' "$PG_CONTAINER")" == healthy ]] || return 1
  docker inspect -f '{{.State.Running}}' "$N8N_CONTAINER" | grep -qx true
  docker inspect -f '{{.State.Running}}' "$NGINX_CONTAINER" | grep -qx true
  curl --fail --silent --show-error --max-time 15 http://127.0.0.1:5678/healthz/readiness >/dev/null
  curl --fail --silent --show-error --max-time 15 http://127.0.0.1:80/ >/dev/null
}

on_exit() {
  local rc=$?
  if ((rc != 0 && MUTATED && ROLLBACK_READY && !ROLLBACK_RUNNING)); then
    echo "Restore failed after modifying: $MODIFIED. Attempting recovery from persistent preventive backup." >&2
    ROLLBACK_RUNNING=1; set +e; restore_payload "$ROLLBACK" "rollback recovery" && health_checks; recovered=$?; set -e
    if ((recovered == 0)); then echo "Recovery completed from the preventive backup." >&2; else echo "Automatic recovery failed; use the persistent backup under backups/pre-restore/." >&2; fi
  elif ((rc != 0)); then echo "Restore stopped before modifying production data (modified: $MODIFIED)." >&2; fi
  rm -rf "$WORK"; exit "$rc"
}
trap on_exit EXIT

# Validate cryptographic integrity and every component before any service is stopped or data is replaced.
gpg --batch --quiet --pinentry-mode loopback --passphrase-file "$KEY_FILE" --decrypt "$BACKUP" > "$WORK/archive.tar.gz"
tar -tzf "$WORK/archive.tar.gz" >/dev/null
if tar -tzf "$WORK/archive.tar.gz" | grep -Eq '(^/|(^|/)\.\.(/|$))'; then echo "Unsafe archive path." >&2; exit 1; fi
tar -xzf "$WORK/archive.tar.gz" -C "$INCOMING"
for file in postgres/n8n.dump postgres/calidad_aire.dump postgres/globals.sql postgres/roles.txt n8n-volume.tar.gz runtime.env docker-compose.yml manifest.txt; do [[ -s "$INCOMING/$file" ]] || { echo "Missing backup component: $file" >&2; exit 1; }; done
grep -qx 'format=ecopredict-backup-v2' "$INCOMING/manifest.txt" || { echo "Unsupported backup format." >&2; exit 1; }
[[ ! -d "$ROOT_DIR/infrastructure/nginx" || -d "$INCOMING/nginx" ]] || { echo "Backup lacks required Nginx configuration." >&2; exit 1; }
old_key="$(grep -E '^N8N_ENCRYPTION_KEY=' "$INCOMING/runtime.env" | head -n1 || true)"; current_key="$(grep -E '^N8N_ENCRYPTION_KEY=' "$ENV_FILE" | head -n1 || true)"
[[ -n "$old_key" && "$old_key" == "$current_key" ]] || { echo "n8n encryption key mismatch; refusing restore to protect encrypted credentials." >&2; exit 1; }
docker inspect "$PG_CONTAINER" >/dev/null; docker volume inspect "$N8N_VOLUME" >/dev/null; docker compose -p "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config -q
docker exec "$PG_CONTAINER" psql -U "$PG_ADMIN" -d postgres -Atqc 'SELECT rolsuper FROM pg_roles WHERE rolname = current_user' | grep -qx t || { echo "PostgreSQL administrator is not a superuser." >&2; exit 1; }
docker exec -i "$PG_CONTAINER" pg_restore -l < "$INCOMING/postgres/n8n.dump" >/dev/null; docker exec -i "$PG_CONTAINER" pg_restore -l < "$INCOMING/postgres/calidad_aire.dump" >/dev/null; tar -tzf "$INCOMING/n8n-volume.tar.gz" >/dev/null
# Existing roles are retained: globals were backed up without passwords, and only compatible role sets are accepted.
current_roles="$(docker exec "$PG_CONTAINER" psql -U "$PG_ADMIN" -d postgres -Atqc 'SELECT rolname FROM pg_roles ORDER BY rolname')"
while IFS= read -r role; do grep -Fxq "$role" <<< "$current_roles" || { echo "Required archived PostgreSQL role is absent; refusing unsafe role overwrite." >&2; exit 1; }; done < "$INCOMING/postgres/roles.txt"
docker exec "$PG_CONTAINER" pg_dumpall -U "$PG_ADMIN" --globals-only --no-role-passwords > "$WORK/current-globals.sql"
# PostgreSQL 16 may add random psql \restrict tokens; normalize only those non-stateful lines before comparison.
sed -e '/^\\restrict /d' -e '/^\\unrestrict /d' "$INCOMING/postgres/globals.sql" > "$WORK/incoming-globals.normalized.sql"
sed -e '/^\\restrict /d' -e '/^\\unrestrict /d' "$WORK/current-globals.sql" > "$WORK/current-globals.normalized.sql"
cmp -s "$WORK/incoming-globals.normalized.sql" "$WORK/current-globals.normalized.sql" || { echo "Global PostgreSQL roles or grants differ; refusing an unsafe overwrite." >&2; exit 1; }
mapfile -t images < <(docker compose -p "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config --images)
for image in "${images[@]}"; do docker image inspect "$image" >/dev/null || { echo "Required image is not local; restore will not pull images: $image" >&2; exit 1; }; done
docker image inspect alpine:3.20 >/dev/null || { echo "Required local helper image alpine:3.20 is unavailable; restore will not pull it." >&2; exit 1; }

# The preventive archive remains outside the temporary directory and is itself validated before mutation.
ROLLBACK_ID="pre-restore-$(date -u +%Y%m%dT%H%M%SZ)"
bash "$ROOT_DIR/scripts/backup.sh" --key-file "$KEY_FILE" --output-dir "$ROOT_DIR/backups/pre-restore" --backup-id "$ROLLBACK_ID" --compose-file "$COMPOSE_FILE" --env-file "$ENV_FILE"
PREVENTIVE="$ROOT_DIR/backups/pre-restore/$ROLLBACK_ID.tar.gz.gpg"; (cd "$(dirname "$PREVENTIVE")" && sha256sum -c "$(basename "$PREVENTIVE").sha256")
gpg --batch --quiet --pinentry-mode loopback --passphrase-file "$KEY_FILE" --decrypt "$PREVENTIVE" | tar -xzf - -C "$ROLLBACK"
for file in postgres/n8n.dump postgres/calidad_aire.dump n8n-volume.tar.gz; do [[ -s "$ROLLBACK/$file" ]] || { echo "Preventive backup validation failed." >&2; exit 1; }; done
ROLLBACK_READY=1; MUTATED=1
restore_payload "$INCOMING" "target database and n8n volume"
health_checks || { echo "One or more services are unhealthy after restore." >&2; exit 1; }
echo "Restore completed. Persistent preventive backup: backups/pre-restore/$ROLLBACK_ID.tar.gz.gpg"
