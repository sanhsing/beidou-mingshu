#!/bin/bash
# 健康檢查腳本

HOST=${MINGSHU_HOST:-localhost}
PORT=${MINGSHU_PORT:-5000}
URL="http://${HOST}:${PORT}/health"

response=$(curl -s -o /dev/null -w "%{http_code}" $URL)

if [ "$response" = "200" ]; then
    echo "✅ 服務正常運行"
    exit 0
else
    echo "❌ 服務異常 (HTTP $response)"
    exit 1
fi
