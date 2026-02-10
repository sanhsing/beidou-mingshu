#!/bin/bash
# ================================================================
# 北斗命數 GitHub 更新腳本 v2.0
# ================================================================
# 使用方式:
#   1. 將此腳本和新文件放在同一目錄
#   2. 執行: ./github_update.sh
# ================================================================

set -e

REPO_URL="git@github.com:sanhsing/beidou-mingshu.git"
# 或使用 HTTPS: https://github.com/sanhsing/beidou-mingshu.git
BRANCH="main"
WORK_DIR="beidou-mingshu"
VERSION="2.0.0"
DATE=$(date +%Y%m%d)

echo "================================================"
echo "北斗命數 GitHub 更新腳本"
echo "版本: $VERSION | 日期: $DATE"
echo "================================================"

# Step 1: 克隆/更新 repo
echo ""
echo "📥 Step 1: 同步 repo..."

if [ -d "$WORK_DIR" ]; then
    cd $WORK_DIR
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
    cd ..
else
    git clone $REPO_URL
fi

# Step 2: 複製新文件
echo ""
echo "📂 Step 2: 更新文件..."

# 核心模組
MODULES=(
    "field_engine_v1.py"
    "mingshu_engine_v1.py"
    "e18k_field_bridge_v1.py"
    "mingshu_suite_v1.py"
    "mingshu_commercial_v1.py"
    "mingshu_naming_marriage_v1.py"
    "mingshu_zeri_db_web_v1.py"
    "mingshu_liunian_hepan_v1.py"
    "mingshu_meihua_pdf_v1.py"
    "mingshu_advanced_v1.py"
    "mingshu_advanced_pylib_v1.py"
    "mingshu_api_unified_v2.py"
)

# 部署文件
DEPLOY_FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "nginx.conf"
    "mingshu.service"
    ".env.template"
    "requirements.txt"
    "deploy.sh"
    "quickstart.sh"
    "health_check.sh"
    "backup.sh"
    "wsgi.py"
    "DEPLOY.md"
)

cd $WORK_DIR

# 複製模組 (如果在上層目錄存在)
for mod in "${MODULES[@]}"; do
    if [ -f "../$mod" ]; then
        cp "../$mod" .
        echo "  ✓ $mod"
    fi
done

# 複製部署文件
for file in "${DEPLOY_FILES[@]}"; do
    if [ -f "../$file" ]; then
        cp "../$file" .
        echo "  ✓ $file"
    fi
done

# Step 3: 更新 README
echo ""
echo "📝 Step 3: 更新 README..."

cat > README.md << 'README'
# 北斗命數 Beidou Mingshu

北斗命數 - 統一命理分析系統 v2.0

## 功能特色

- 🎯 **統一引擎**: 八字、紫微、易經、場論一體化
- 🔮 **進階術數**: 四化飛星、奇門遁甲、六壬神課、風水羅盤
- 💼 **商用就緒**: 完整 API、認證、日誌、監控
- 🐳 **容器部署**: Docker 一鍵部署

## 快速開始

### 方式一：快速啟動

```bash
./quickstart.sh
```

### 方式二：Docker 部署

```bash
cp .env.template .env
# 編輯 .env 設置密鑰
./deploy.sh docker
```

## API 端點

| 層級 | 價格 | 端點數 | 功能 |
|------|------|--------|------|
| 基本版 | NT$69/月 | 9 | 八字、紫微、姓名、梅花、流年 |
| 專業版 | NT$199/月 | 11 | 命名、合婚、擇日、PDF報告 |
| 進階版 | NT$399/月 | 6 | 四化、奇門、六壬、風水 |

## 模組清單

| 模組 | 行數 | 說明 |
|------|------|------|
| mingshu_api_unified_v2.py | 818 | 統一 API 入口 |
| mingshu_engine_v1.py | 1,195 | 核心命數引擎 |
| mingshu_commercial_v1.py | 1,454 | 商用套件 |
| mingshu_advanced_pylib_v1.py | 1,334 | D1-D4 進階術數 |
| field_engine_v1.py | 1,253 | 場論引擎 |
| ... | ... | 共 12 模組 |

**總計: 13,549 行**

## 技術架構

```
統一API入口 (mingshu_api_unified_v2.py)
├── 基本版 (9端點)
│   └── 八字/紫微/姓名/梅花/流年/場態
├── 專業版 (11端點)
│   └── 易經/命名/合婚/擇日/PDF
├── 進階版 (6端點)
│   └── 四化/奇門/六壬/風水
└── 基礎設施
    └── 驗證/日誌/認證/配置/監控
```

## 部署說明

詳見 [DEPLOY.md](DEPLOY.md)

## 版權聲明

© 2026 北斗七星文創數位
README

echo "  ✓ README.md"

# Step 4: Git 操作
echo ""
echo "📤 Step 4: 提交更新..."

git add -A

# 檢查是否有變更
if git diff --staged --quiet; then
    echo "  ℹ️  沒有需要提交的變更"
else
    git commit -m "🚀 Update to v$VERSION - $DATE

- 新增 D1-D4 進階術數模組
- 更新統一 API 入口 v2
- 新增 Docker 部署配置
- 優化商用套件
- 總計 13,549 行程式碼
"
    
    echo ""
    echo "📤 Step 5: 推送到 GitHub..."
    git push origin $BRANCH
    
    echo ""
    echo "================================================"
    echo "✅ 更新完成!"
    echo "   Repo: https://github.com/sanhsing/beidou-mingshu"
    echo "   版本: $VERSION"
    echo "================================================"
fi
