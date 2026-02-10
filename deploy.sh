#!/bin/bash
# 北斗命數部署腳本
# 使用: ./deploy.sh [docker|systemd|dev]

set -e

MODE=${1:-docker}
PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)

echo "================================================"
echo "北斗命數部署腳本 v2.0"
echo "模式: $MODE"
echo "================================================"

# 檢查環境
check_env() {
    if [ ! -f ".env" ]; then
        echo "⚠️  .env 文件不存在，從模板創建..."
        cp .env.template .env
        echo "⚠️  請編輯 .env 文件設置密鑰！"
    fi
}

# Docker 部署
deploy_docker() {
    echo "🐳 Docker 部署中..."
    
    check_env
    
    # 構建映像
    docker-compose build
    
    # 啟動服務
    docker-compose up -d
    
    echo "✅ Docker 部署完成"
    echo "   訪問: http://localhost:${MINGSHU_PORT:-5000}"
    echo "   日誌: docker-compose logs -f"
}

# systemd 部署
deploy_systemd() {
    echo "🔧 systemd 部署中..."
    
    # 創建用戶
    if ! id "mingshu" &>/dev/null; then
        sudo useradd -r -s /bin/false mingshu
    fi
    
    # 創建目錄
    sudo mkdir -p /opt/mingshu/{data,logs,backups}
    sudo cp -r . /opt/mingshu/
    sudo chown -R mingshu:mingshu /opt/mingshu
    
    # 創建虛擬環境
    sudo -u mingshu python3 -m venv /opt/mingshu/venv
    sudo -u mingshu /opt/mingshu/venv/bin/pip install -r /opt/mingshu/requirements.txt
    
    # 安裝服務
    sudo cp mingshu.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable mingshu
    sudo systemctl start mingshu
    
    echo "✅ systemd 部署完成"
    echo "   狀態: sudo systemctl status mingshu"
    echo "   日誌: sudo journalctl -u mingshu -f"
}

# 開發模式
deploy_dev() {
    echo "🔨 開發模式啟動..."
    
    check_env
    
    # 安裝依賴
    pip install -r requirements.txt
    
    # 啟動
    export FLASK_ENV=development
    python mingshu_api_unified_v2.py --serve 5000
}

# 主程序
case $MODE in
    docker)
        deploy_docker
        ;;
    systemd)
        deploy_systemd
        ;;
    dev)
        deploy_dev
        ;;
    *)
        echo "用法: ./deploy.sh [docker|systemd|dev]"
        exit 1
        ;;
esac
