#!/bin/bash
# 快速啟動腳本 (開發/測試用)

echo "北斗命數 API v2.0 快速啟動"
echo "=========================="

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3"
    exit 1
fi

# 安裝依賴
pip install -q flask requests python-dateutil

# 啟動
echo "🚀 啟動服務..."
python3 mingshu_api_unified_v2.py --serve 5000
