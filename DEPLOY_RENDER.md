# 北斗命數 Render 部署指南

**版本**：v1.0.0  
**日期**：2026-02-18

---

## 一、前置準備

### 1.1 必要帳號
- [x] Render 帳號 (https://render.com)
- [x] GitHub 帳號（用於連接倉庫）
- [ ] 綠界正式商店帳號（可後續設置）

### 1.2 本地準備
```bash
# 解壓部署包
unzip beidou_mingshu_deploy_20260218.zip
cd beidou_mvp
```

---

## 二、GitHub 設置

### 2.1 創建私有倉庫
1. GitHub → New Repository
2. 名稱：`beidou-mingshu`
3. 可見性：**Private**

### 2.2 推送代碼
```bash
git init
git add .
git commit -m "Initial: 北斗命數 v1.0.0"
git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/beidou-mingshu.git
git push -u origin main
```

---

## 三、Render 部署

### 3.1 創建 Web Service
1. Render Dashboard → **New** → **Web Service**
2. 連接 GitHub 倉庫 `beidou-mingshu`
3. 配置：

| 設置 | 值 |
|------|-----|
| Name | `beidou-mingshu` |
| Region | Singapore |
| Branch | main |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| Plan | Starter ($7/月) 或 Free |

### 3.2 環境變數
在 Render Dashboard → Environment 設置：

```
SECRET_KEY=<生成一個隨機字串>
DATABASE_URL=sqlite:///./beidou_unified.db
ECPAY_SANDBOX=true
APP_ENV=production
DEBUG=false
```

### 3.3 部署
點擊 **Create Web Service** → 等待部署完成

---

## 四、驗證部署

### 4.1 健康檢查
```
https://beidou-mingshu.onrender.com/api/health
```

### 4.2 首頁
```
https://beidou-mingshu.onrender.com/
```

### 4.3 API 文檔
```
https://beidou-mingshu.onrender.com/docs
```

---

## 五、綠界支付設置（上線後）

### 5.1 申請正式商店
- 綠界官網：https://www.ecpay.com.tw/
- 申請「網路特店」

### 5.2 更新環境變數
```
ECPAY_MERCHANT_ID=<正式商店編號>
ECPAY_HASH_KEY=<正式 HashKey>
ECPAY_HASH_IV=<正式 HashIV>
ECPAY_SANDBOX=false
```

---

## 六、自訂域名（可選）

### 6.1 購買域名
建議：`beidou-mingshu.com` 或 `mingshu.tw`

### 6.2 Render 設置
1. Dashboard → Settings → Custom Domains
2. 添加域名
3. 配置 DNS CNAME

---

## 七、監控

### 7.1 Sentry 錯誤追蹤
1. 註冊 Sentry (https://sentry.io)
2. 創建 Python 項目
3. 添加環境變數：`SENTRY_DSN=<your-dsn>`

---

*北斗七星文創數位 © 2026*
