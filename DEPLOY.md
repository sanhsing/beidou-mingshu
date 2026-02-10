# 北斗命數部署指南

## 快速部署

### 方式一：Docker (推薦)

```bash
# 1. 配置環境變量
cp .env.template .env
nano .env  # 修改 MINGSHU_SECRET_KEY

# 2. 部署
./deploy.sh docker

# 3. 查看狀態
docker-compose ps
docker-compose logs -f
```

### 方式二：systemd

```bash
# 需要 root 權限
sudo ./deploy.sh systemd

# 查看狀態
sudo systemctl status mingshu
sudo journalctl -u mingshu -f
```

### 方式三：開發模式

```bash
./deploy.sh dev
```

## 配置說明

### 環境變量

| 變量 | 說明 | 默認值 |
|------|------|--------|
| MINGSHU_PORT | 服務端口 | 5000 |
| MINGSHU_SECRET_KEY | 密鑰 (必改!) | - |
| MINGSHU_DB_PATH | 資料庫路徑 | ./data/mingshu.db |
| MINGSHU_LOG_LEVEL | 日誌級別 | INFO |

### 端點

| 端點 | 說明 |
|------|------|
| / | 系統概覽 |
| /health | 健康檢查 |
| /api/status | API 狀態 |
| /api/pricing | 定價方案 |
| /docs | API 文檔 |

## 維護命令

```bash
# 重啟服務 (Docker)
docker-compose restart

# 查看日誌
docker-compose logs -f mingshu

# 備份
./backup.sh

# 健康檢查
./health_check.sh
```

## 生產環境清單

- [ ] 修改 MINGSHU_SECRET_KEY
- [ ] 配置 HTTPS (SSL 證書)
- [ ] 設置防火牆規則
- [ ] 配置日誌輪轉
- [ ] 設置定時備份 (crontab)
- [ ] 配置監控告警

## 定時備份 (crontab)

```bash
# 每天凌晨 3 點備份
0 3 * * * /opt/mingshu/backup.sh >> /opt/mingshu/logs/backup.log 2>&1
```

## 聯繫方式

北斗七星文創數位
