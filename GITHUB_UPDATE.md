# 北斗命數 v2.0.0 更新說明

## Commit Message (複製使用)

```
🚀 北斗命數 v2.0.0 - 新增進階術數 D1-D4

## 新增功能
- D1 紫微四化飛星：本命四化、宮干飛星、自化分析
- D2 奇門遁甲：時盤排盤、格局判斷、八門九星
- D3 六壬神課：四課三傳、十二神將、場論整合
- D4 風水羅盤：二十四山、三元九運、坐向分析

## 模組更新
- 新增 mingshu_advanced_v1.py (1,285行)
- 新增 mingshu_advanced_pylib_v1.py (1,334行)
- 更新 mingshu_api_unified_v2.py (818行)

## 部署配置
- 新增 Docker 部署 (Dockerfile, docker-compose.yml)
- 新增 Nginx 反向代理配置
- 新增 systemd 服務配置
- 新增一鍵部署腳本

## API 端點
- 基本版: 9 端點 (NT$69/月)
- 專業版: 11 端點 (NT$199/月)
- 進階版: 6 端點 (NT$399/月)
- 總計: 26 個 API 端點

## 統計
- 模組數: 12 個
- 程式碼: 13,549 行
- 引擎: 8/8 可用
```

---

## 本地更新步驟

```bash
# 1. 進入你的本地 repo 目錄
cd ~/beidou-mingshu
# 或克隆
# git clone https://github.com/sanhsing/beidou-mingshu.git

# 2. 確保在 main 分支
git checkout main
git pull origin main

# 3. 下載並解壓 mingshu_deploy_v2.zip
# 將解壓後的文件複製到 repo 目錄

# 4. 查看變更
git status
git diff

# 5. 添加所有文件
git add -A

# 6. 提交 (使用上面的 commit message)
git commit -m "🚀 北斗命數 v2.0.0 - 新增進階術數 D1-D4"

# 7. 推送
git push origin main

# 8. 驗證
# 訪問 https://github.com/sanhsing/beidou-mingshu
```

---

## 文件變更清單

### 新增文件
| 文件 | 說明 |
|------|------|
| mingshu_advanced_v1.py | D1-D4 基礎版 |
| mingshu_advanced_pylib_v1.py | D1-D4 場論增強版 |
| mingshu_api_unified_v2.py | 統一 API v2 |
| Dockerfile | Docker 映像配置 |
| docker-compose.yml | Docker Compose |
| nginx.conf | Nginx 配置 |
| mingshu.service | systemd 服務 |
| .env.template | 環境變量模板 |
| deploy.sh | 部署腳本 |
| quickstart.sh | 快速啟動 |
| health_check.sh | 健康檢查 |
| backup.sh | 備份腳本 |
| wsgi.py | Gunicorn 入口 |
| DEPLOY.md | 部署文檔 |

### 更新文件
| 文件 | 變更 |
|------|------|
| README.md | 更新版本說明 |
| requirements.txt | 更新依賴 |

---

## 版本歷史

| 版本 | 日期 | 說明 |
|------|------|------|
| v2.0.0 | 2026-02-11 | 新增 D1-D4 進階術數、Docker 部署 |
| v1.0.0 | 2026-02-10 | 基本版+專業版完整功能 |
