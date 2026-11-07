#!/usr/bin/env bash
# Git Bash helper for an intentional local Docker restore.
set -Eeuo pipefail
BACKUP="${1:-}"; KEY_FILE="${2:-${BACKUP_ENCRYPTION_KEY_FILE:-}}"
[[ -r "$BACKUP" && -r "$KEY_FILE" ]] || { echo 'Usage: bash scripts/restore-local.sh BACKUP.gpg KEY_FILE' >&2; exit 2; }
read -r -p "This will replace local n8n and PostgreSQL data. Type RESTORE_LOCAL: " answer
[[ "$answer" == RESTORE_LOCAL ]] || { echo 'Cancelled.'; exit 1; }
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bash "$ROOT_DIR/scripts/restore.sh" --backup-file "$BACKUP" --key-file "$KEY_FILE" --confirm RESTORE
