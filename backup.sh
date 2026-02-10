#!/bin/bash
# 備份腳本

BACKUP_DIR=${MINGSHU_BACKUP_PATH:-./backups}
DATA_DIR=${MINGSHU_DATA_PATH:-./data}
KEEP_DAYS=${MINGSHU_BACKUP_KEEP_DAYS:-30}
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 備份資料庫
if [ -f "$DATA_DIR/mingshu.db" ]; then
    cp "$DATA_DIR/mingshu.db" "$BACKUP_DIR/mingshu_$DATE.db"
    gzip "$BACKUP_DIR/mingshu_$DATE.db"
    echo "✅ 備份完成: mingshu_$DATE.db.gz"
fi

# 清理舊備份
find $BACKUP_DIR -name "*.gz" -mtime +$KEEP_DAYS -delete
echo "✅ 已清理 $KEEP_DAYS 天前的備份"
