# 北斗命數部署指南
> 版本：v1.0.0 | 日期：2026-02-17 | @澄書

## 📋 目錄

- [環境要求](#環境要求)
- [本地部署](#本地部署)
- [Docker 部署](#docker-部署)
- [生產環境](#生產環境)

---

## 🖥️ 環境要求

| 項目 | 最低要求 | 建議配置 |
|------|----------|----------|
| CPU | 1 核心 | 2+ 核心 |
| 記憶體 | 512MB | 2GB+ |
| Python | 3.11+ | 3.11 |

---

## 🚀 本地部署

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 配置環境變數

```bash
cp .env.example .env
# 編輯 .env，修改 JWT_SECRET
```

### 3. 啟動服務

```bash
python app.py
# 或
./start.sh dev
```

### 4. 驗證

```bash
curl http://localhost:8000/api/health
```

---

## 🐳 Docker 部署

```bash
# 建構
docker build -t beidou-mingshu .

# 啟動
docker-compose up -d

# 日誌
docker-compose logs -f
```

---

## 🌐 生產環境

### Nginx 反向代理

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Systemd 服務

```ini
[Unit]
Description=BeiDou MingShu API

[Service]
WorkingDirectory=/opt/beidou
ExecStart=/opt/beidou/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🔧 環境變數

| 變數 | 必須 | 說明 |
|------|:----:|------|
| `JWT_SECRET` | ✅ | JWT 密鑰（必改） |
| `DB_PATH` | ❌ | 數據庫路徑 |
| `ECPAY_SANDBOX` | ❌ | 綠界測試模式 |

---

*@澄書 | XTF Task Chain D2*
