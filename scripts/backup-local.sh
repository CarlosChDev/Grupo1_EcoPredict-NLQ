#!/usr/bin/env bash
# Git Bash helper: retain an encrypted copy locally from OCI or Cloudflare R2.
set -Eeuo pipefail
umask 077
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; DEST="$ROOT_DIR/backups"
mode="${1:-}"; mkdir -p "$DEST"
[[ -n "$mode" ]] || { read -r -p 'Source [oci/r2]: ' mode; }
case "$mode" in
oci|--from-oci)
  : "${OCI_HOST:?OCI_HOST is required}" "${OCI_USER:?OCI_USER is required}" "${OCI_SSH_KEY_FILE:?OCI_SSH_KEY_FILE is required}" "${OCI_KNOWN_HOSTS_FILE:?OCI_KNOWN_HOSTS_FILE is required}" "${BACKUP_ENCRYPTION_KEY_FILE:?BACKUP_ENCRYPTION_KEY_FILE is required}"
  opts=(-i "$OCI_SSH_KEY_FILE" -o "UserKnownHostsFile=$OCI_KNOWN_HOSTS_FILE" -o StrictHostKeyChecking=yes)
  remote="/tmp/ecopredict-backup-$RANDOM-$RANDOM"; ssh "${opts[@]}" "$OCI_USER@$OCI_HOST" "mkdir -m 700 '$remote'"
  trap 'ssh "${opts[@]}" "$OCI_USER@$OCI_HOST" "rm -rf -- \"$remote\"" >/dev/null 2>&1 || true' EXIT
  scp "${opts[@]}" "$BACKUP_ENCRYPTION_KEY_FILE" "$OCI_USER@$OCI_HOST:$remote/key"
  ssh "${opts[@]}" "$OCI_USER@$OCI_HOST" "chmod 600 '$remote/key'; cd /home/ubuntu/Grupo1_EcoPredict-NLQ && bash scripts/backup.sh --key-file '$remote/key' --output-dir '$remote'"
  name="$(ssh "${opts[@]}" "$OCI_USER@$OCI_HOST" "find '$remote' -maxdepth 1 -name 'ecopredict-*.tar.gz.gpg' -printf '%f\\n'" | tail -n1)"; [[ -n "$name" ]] || exit 1
  scp "${opts[@]}" "$OCI_USER@$OCI_HOST:$remote/$name" "$OCI_USER@$OCI_HOST:$remote/$name.sha256" "$DEST/"; (cd "$DEST" && sha256sum -c "$name.sha256");;
r2|--from-r2)
  : "${R2_ACCESS_KEY_ID:?R2_ACCESS_KEY_ID is required}" "${R2_SECRET_ACCESS_KEY:?R2_SECRET_ACCESS_KEY is required}" "${R2_ENDPOINT:?R2_ENDPOINT is required}" "${R2_BUCKET:?R2_BUCKET is required}"
  command -v aws >/dev/null || { echo 'AWS CLI is required for R2.' >&2; exit 127; }
  export AWS_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID" AWS_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY" AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-auto}" AWS_EC2_METADATA_DISABLED=true
  mapfile -t items < <(aws --endpoint-url "$R2_ENDPOINT" s3api list-objects-v2 --bucket "$R2_BUCKET" --query "sort_by(Contents[?ends_with(Key, '.tar.gz.gpg')],&LastModified)[].Key" --output text | tr '\t' '\n' | awk 'NF && $1 != "None"')
  ((${#items[@]})) || { echo 'No encrypted backups found.' >&2; exit 1; }; select name in "${items[@]}"; do [[ -n "$name" ]] && break; done
  [[ "$name" =~ ^ecopredict-[A-Za-z0-9._-]+\.tar\.gz\.gpg$ ]] || { echo 'Invalid backup selection.' >&2; exit 1; }
  aws --endpoint-url "$R2_ENDPOINT" s3 cp "s3://$R2_BUCKET/$name" "$DEST/$name" >/dev/null; aws --endpoint-url "$R2_ENDPOINT" s3 cp "s3://$R2_BUCKET/$name.sha256" "$DEST/$name.sha256" >/dev/null; (cd "$DEST" && sha256sum -c "$name.sha256");;
*) echo 'Usage: bash scripts/backup-local.sh --from-oci|--from-r2' >&2; exit 2;; esac
echo "Encrypted local copy verified in: $DEST"
