#!/bin/bash
# ==========================================
# Script de Respaldo Local - EcoPredict
# ==========================================

BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ecopredict_local_backup_$TIMESTAMP.sql"

echo "[INFO] Iniciando respaldo local de la base de datos..."

# Usando el usuario y base de datos configurados en tu docker-compose (.env)
MSYS_NO_PATHCONV=1 docker exec -t aire_postgres pg_dump -U n8n_user n8n > "$BACKUP_FILE"

if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    echo "[SUCCESS] ¡Respaldo local completado con éxito!"
    echo "[FILE] Archivo generado en: $BACKUP_FILE"
else
    echo "[ERROR] El archivo de respaldo está vacío o falló la extracción."
    exit 1
fi