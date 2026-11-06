#!/bin/bash
# ==========================================
# Script de Restauración Local - EcoPredict
# ==========================================

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "[ERROR] Debes especificar la ruta del archivo .sql de respaldo."
    echo "Uso: ./scripts/restore.sh ./backups/tu_archivo.sql"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "[ERROR] El archivo $BACKUP_FILE no existe."
    exit 1
fi

echo "[WARNING] Estás a punto de sobrescribir la base de datos local con: $BACKUP_FILE"
read -p "¿Deseas continuar? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "[INFO] Restaurando base de datos en el contenedor local..."
    
    MSYS_NO_PATHCONV=1 docker exec -i aire_postgres psql -U n8n_user -d n8n < "$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo "[SUCCESS] ¡Base de datos restaurada satisfactoriamente!"
    else
        echo "[ERROR] Hubo un problema durante la restauración local."
        exit 1
    fi
else
    echo "[INFO] Operación cancelada por el usuario."
fi