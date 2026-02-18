#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# 北斗命數啟動腳本
# 版本：v1.0.0
# ═══════════════════════════════════════════════════════════════════

set -e

# 顏色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🌟 北斗命數 SaaS 系統${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安裝${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"

# 檢查虛擬環境
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ 虛擬環境存在${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${GREEN}✓ 虛擬環境存在${NC}"
    source .venv/bin/activate
fi

# 檢查依賴
echo -e "\n${YELLOW}檢查依賴...${NC}"
pip install -q -r requirements.txt 2>/dev/null || {
    echo -e "${YELLOW}安裝依賴中...${NC}"
    pip install -r requirements.txt
}
echo -e "${GREEN}✓ 依賴已安裝${NC}"

# 檢查 .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 不存在，從 .env.example 複製...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env 已創建${NC}"
    else
        echo -e "${RED}❌ .env.example 不存在${NC}"
    fi
fi

# 解析參數
MODE=${1:-"dev"}
PORT=${2:-8000}

case $MODE in
    dev|development)
        echo -e "\n${YELLOW}🔧 開發模式${NC}"
        export DEBUG=true
        export ENV=development
        python3 app.py
        ;;
    prod|production)
        echo -e "\n${YELLOW}🚀 生產模式${NC}"
        export DEBUG=false
        export ENV=production
        uvicorn app:app --host 0.0.0.0 --port $PORT --workers 4
        ;;
    test)
        echo -e "\n${YELLOW}🧪 測試模式${NC}"
        python3 -m pytest tests/ -v
        ;;
    check)
        echo -e "\n${YELLOW}🔍 檢查模式${NC}"
        python3 -c "
from app import app, get_all_routes
routes = get_all_routes()
print(f'✅ 路由數量: {len(routes)}')
api_routes = [r for r in routes if r[1].startswith('/api')]
print(f'✅ API 端點: {len(api_routes)}')
"
        ;;
    *)
        echo -e "${YELLOW}使用方式:${NC}"
        echo "  ./start.sh dev      # 開發模式"
        echo "  ./start.sh prod     # 生產模式"
        echo "  ./start.sh test     # 運行測試"
        echo "  ./start.sh check    # 檢查路由"
        ;;
esac

echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
