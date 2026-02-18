# 北斗命數 API 文檔
> 版本：v1.0.0 | 基礎 URL：`http://localhost:8000`

## 📋 目錄

- [認證 API](#認證-api)
- [命理 API](#命理-api)
- [PDF 報告 API](#pdf-報告-api)
- [支付 API](#支付-api)
- [用戶數據 API](#用戶數據-api)
- [系統 API](#系統-api)

---

## 🔐 認證 API

### POST /api/auth/register
註冊新用戶

**請求：**
```json
{
  "username": "testuser",
  "password": "password123",
  "email": "test@example.com"
}
```

**回應：**
```json
{
  "success": true,
  "message": "註冊成功",
  "user": {
    "id": 1,
    "username": "testuser",
    "credits": 100
  }
}
```

---

### POST /api/auth/login
用戶登入

**請求：**
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**回應：**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "username": "testuser",
    "credits": 100,
    "tier": "free"
  }
}
```

---

### GET /api/auth/me
獲取當前用戶資訊（需認證）

**Headers：**
```
Authorization: Bearer {token}
```

**回應：**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "credits": 100,
  "tier": "free",
  "created_at": "2026-02-17T10:00:00"
}
```

---

## 🔮 命理 API

### POST /api/bazi/analyze
八字分析

**請求：**
```json
{
  "year": 1990,
  "month": 6,
  "day": 15,
  "hour": 12,
  "gender": "男",
  "calendar": "solar"
}
```

**回應：**
```json
{
  "四柱": {
    "年柱": "庚午",
    "月柱": "壬午",
    "日柱": "甲子",
    "時柱": "庚午"
  },
  "日主": {
    "天干": "甲",
    "五行": "木"
  },
  "用神喜忌": {
    "用神": "水",
    "喜神": "金",
    "忌神": "火"
  },
  "五行統計": {
    "木": 1,
    "火": 3,
    "土": 0,
    "金": 2,
    "水": 2
  }
}
```

---

### POST /api/ziwei/chart
紫微斗數排盤

**請求：**
```json
{
  "year": 1990,
  "month": 6,
  "day": 15,
  "hour": 12,
  "gender": "男",
  "calendar": "solar"
}
```

**回應：**
```json
{
  "命宮": "子女",
  "身宮": "遷移",
  "局數": 5,
  "命主星": ["紫微", "天府"],
  "十二宮": {
    "命宮": {"位置": "子女", "主星": ["紫微"]},
    ...
  }
}
```

---

### POST /api/meihua/divine
梅花易數起卦

**請求：**
```json
{
  "method": "time",
  "question": "今日運勢如何？"
}
```

**回應：**
```json
{
  "本卦": "天火同人",
  "變卦": "乾為天",
  "互卦": "天風姤",
  "動爻": 3,
  "體卦": "離",
  "用卦": "乾",
  "斷語": "..."
}
```

---

### POST /api/date/select
擇日選擇

**請求：**
```json
{
  "date_type": "marry",
  "year": 2026,
  "month": 3,
  "bazi": {
    "year": 1990, "month": 6, "day": 15, "hour": 12
  }
}
```

**回應：**
```json
{
  "推薦日期": [
    {
      "date": "2026-03-08",
      "score": 92,
      "日課": "丙寅年 辛卯月 甲子日",
      "宜忌": ["宜嫁娶", "宜納采"]
    }
  ]
}
```

---

### POST /api/match
合婚分析

**請求：**
```json
{
  "person1": {
    "year": 1990, "month": 6, "day": 15, "hour": 12, "gender": "男"
  },
  "person2": {
    "year": 1992, "month": 3, "day": 20, "hour": 8, "gender": "女"
  }
}
```

**回應：**
```json
{
  "score": 85,
  "grade": "A",
  "summary": "八字相合度高，適合婚配",
  "factors": [
    {"name": "年柱合", "score": 90},
    {"name": "日柱合", "score": 80}
  ]
}
```

---

## 📄 PDF 報告 API

### POST /api/pdf/bazi
生成八字 PDF 報告

**請求：**
```json
{
  "year": 1990,
  "month": 6,
  "day": 15,
  "hour": 12,
  "gender": "男",
  "name": "測試用戶",
  "level": "L1"
}
```

**回應：**
```json
{
  "success": true,
  "file_url": "/reports/bazi_20260217_001.pdf",
  "credits_used": 50
}
```

**報告等級：**
| 等級 | 點數 | 內容 |
|:----:|:----:|------|
| L1 | 50 | 基礎八字分析 |
| L2 | 150 | 完整八字+紫微 |
| L3 | 500 | 全套+諮詢 |

---

### POST /api/pdf/ziwei
生成紫微斗數 PDF 報告

### POST /api/pdf/marry
生成嫁娶擇日 PDF 報告

### POST /api/pdf/match
生成合婚 PDF 報告

### POST /api/pdf/meihua
生成梅花易數 PDF 報告

---

## 💰 支付 API

### GET /api/payment/plans
獲取定價方案

**回應：**
```json
{
  "report_plans": {
    "L1": {"name": "入門版", "price": 2800, "credits": 50},
    "L2": {"name": "進階版", "price": 8800, "credits": 150},
    "L3": {"name": "顧問版", "price": 28000, "credits": 500}
  },
  "credit_plans": {
    "credit_100": {"name": "100點", "price": 100, "credits": 100},
    "credit_500": {"name": "500點", "price": 450, "credits": 500}
  }
}
```

---

### POST /api/payment/create
建立付款訂單

**請求：**
```json
{
  "plan_code": "credit_500",
  "provider": "ecpay"
}
```

**回應：**
```json
{
  "success": true,
  "order_no": "BD20260217001",
  "amount": 450,
  "payment_url": "https://payment.ecpay.com.tw/..."
}
```

---

### POST /api/payment/notify
支付回調（第三方呼叫）

---

## 👤 用戶數據 API

### POST /api/profile
添加出生資料

**請求：**
```json
{
  "name": "張三",
  "gender": "男",
  "birth_year": 1990,
  "birth_month": 6,
  "birth_day": 15,
  "birth_hour": 12,
  "profile_type": "self"
}
```

---

### GET /api/profiles
獲取用戶所有出生資料

---

### GET /api/credits
查詢點數餘額

---

### POST /api/record/save
保存命理記錄

---

### GET /api/records/{type}
獲取歷史記錄

**type 可選值：** `bazi`, `ziwei`, `meihua`, `date`, `match`, `report`

---

## ⚙️ 系統 API

### GET /api/status
系統狀態

```json
{
  "success": true,
  "status": "running",
  "version": "1.0.0",
  "env": "production"
}
```

---

### GET /api/health
健康檢查

```json
{
  "status": "healthy",
  "timestamp": "2026-02-17T10:00:00"
}
```

---

### GET /api/config/plans
獲取定價配置

---

## 🔑 認證說明

需要認證的 API 請在 Headers 中加入：

```
Authorization: Bearer {access_token}
```

Token 有效期：24 小時

---

## ❌ 錯誤碼

| 狀態碼 | 說明 |
|:------:|------|
| 400 | 請求參數錯誤 |
| 401 | 未認證或 Token 失效 |
| 403 | 無權限 |
| 404 | 資源不存在 |
| 500 | 伺服器錯誤 |

---

*文檔由 @澄書 生成 | XTF Task Chain D1*
