# 北斗命數 MVP v3.0 部署指南

## 更新現有 Render 服務

### 方法一：GitHub 自動部署（推薦）

如果已連接 GitHub，推送即自動部署：

```bash
# 1. 進入本地倉庫
cd beidou-mingshu  # 或你的倉庫目錄

# 2. 拉取最新（避免衝突）
git pull origin main

# 3. 複製新版本檔案（覆蓋舊的）
cp -r /path/to/beidou_mvp/* .

# 4. 提交推送
git add .
git commit -m "升級到 MVP v3.0 - 康熙筆畫庫+384爻完整"
git push origin main

# Render 會自動檢測並重新部署
```

### 方法二：Render 手動部署

1. 登入 https://dashboard.render.com
2. 找到 `beidou-mingshu` 服務
3. 點擊 "Manual Deploy" → "Deploy latest commit"

### 方法三：從零部署

```bash
# 1. 初始化 Git
cd beidou_mvp
git init
git add .
git commit -m "北斗命數 MVP v3.0"

# 2. 創建 GitHub Repo
# 到 https://github.com/new 創建 beidou-mingshu

# 3. 推送
git remote add origin https://github.com/YOUR_USERNAME/beidou-mingshu.git
git branch -M main
git push -u origin main

# 4. 在 Render 連接此 Repo
# https://dashboard.render.com → New → Web Service → Connect Repo
```

---

## 部署後驗證

訪問以下端點確認部署成功：

| 端點 | 說明 |
|------|------|
| `/` | 前端首頁 |
| `/docs` | API 文檔（Swagger） |
| `/api/info` | 系統資訊 |
| `/api/v1/bazi` | 八字 API |

---

## 環境變數（可選）

| 變數 | 說明 | 預設值 |
|------|------|--------|
| PORT | 服務端口 | 8000 |
| DEBUG | 調試模式 | false |

---

*北斗命數 MVP v3.0 | 2026.02.17*
