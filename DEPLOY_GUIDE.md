# 北斗命數 SaaS - 正式部署指南

> 更新: 2026-02-17
> 狀態: 準備就緒 ✅

---

## ✅ 前置檢查

| 項目 | 狀態 | 值 |
|------|:----:|-----|
| 綠界正式帳號 | ✅ | 3483910 |
| 域名 | ✅ | beidou-digital.com |
| 測試通過率 | ✅ | 100% |
| .env 配置 | ✅ | 正式環境 |

---

## 🚀 部署步驟

### 方案 A: Render (推薦)

**1. 建立服務**
```
1. 登入 render.com
2. New → Web Service
3. 連接 GitHub repo 或上傳代碼
```

**2. 設定環境變數**
```
SECRET_KEY=5e69f0aaf8efd0f6e4fb37cf274ada4c0eb9bfd3dbb0d9901b8ff8a16b5c56c5
ECPAY_MERCHANT_ID=3483910
ECPAY_HASH_KEY=MyEd25wcb3lfsVmz
ECPAY_HASH_IV=PyXEe6LBfAxFtKZd
ECPAY_SANDBOX=false
SITE_URL=https://beidou-digital.com
```

**3. 設定啟動命令**
```
uvicorn app:app --host 0.0.0.0 --port $PORT
```

**4. 部署完成後，在 Render 設定 Custom Domain**
```
beidou-digital.com
```

### 方案 B: Railway

```bash
# 安裝 CLI
npm i -g @railway/cli

# 登入
railway login

# 初始化專案
railway init

# 部署
railway up
```

---

## 🌐 Namecheap DNS 設定

登入 Namecheap → Domain List → Manage → Advanced DNS

### Render 設定:
```
Type    Host    Value                           TTL
────────────────────────────────────────────────────
A       @       216.24.57.1                     Auto
CNAME   www     your-app.onrender.com           Auto
```

### Railway 設定:
```
Type    Host    Value                           TTL
────────────────────────────────────────────────────
CNAME   @       your-app.up.railway.app         Auto
CNAME   www     your-app.up.railway.app         Auto
```

---

## 🔒 SSL 證書

- **Render**: 自動設定 Let's Encrypt
- **Railway**: 自動設定

無需手動操作。

---

## 📋 部署後檢查清單

```
[ ] 首頁可訪問 https://beidou-digital.com
[ ] 免費試算功能正常 /free
[ ] 註冊/登入功能正常
[ ] 購買頁面正常 /checkout
[ ] 綠界支付跳轉正常
[ ] 支付回調正常 /api/payment/notify
[ ] 點數入帳正常
```

---

## 🔍 綠界回調設定

確保綠界後台的回調 URL 設定為：

```
通知 URL: https://beidou-digital.com/api/payment/notify
返回 URL: https://beidou-digital.com/checkout/return
```

---

## 📊 監控 (可選)

### GA4
```
1. 建立 GA4 帳號
2. 取得 G-XXXXXXXX
3. 更新環境變數 GA4_ID
```

### Sentry
```
1. 建立 Sentry 專案
2. 取得 DSN
3. 更新環境變數 SENTRY_DSN
```

---

## 🆘 故障排除

### 支付失敗
1. 檢查 MerchantID 是否正確
2. 檢查 HashKey/HashIV 是否正確
3. 檢查 ECPAY_SANDBOX 是否為 false
4. 檢查回調 URL 是否可訪問

### 網站無法訪問
1. 檢查 DNS 是否生效 (可能需要 24 小時)
2. 檢查 SSL 是否已設定
3. 檢查服務是否正常運行

---

*北斗命數 SaaS 部署指南 v1.0*
*2026-02-17*
