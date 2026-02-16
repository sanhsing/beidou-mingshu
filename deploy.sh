#!/bin/bash
# 北斗命數 MVP v3.0 一鍵部署腳本

echo "=========================================="
echo "北斗命數 MVP v3.0 部署腳本"
echo "=========================================="

# 檢查 git
if ! command -v git &> /dev/null; then
    echo "❌ 請先安裝 git"
    exit 1
fi

# 檢查是否在 git 倉庫中
if [ -d ".git" ]; then
    echo "📦 檢測到現有 Git 倉庫"
    
    # 拉取最新
    echo "📥 拉取最新代碼..."
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null
    
    # 添加所有更改
    echo "📝 添加更改..."
    git add .
    
    # 提交
    echo "💾 提交更改..."
    git commit -m "升級到 MVP v3.0 - 康熙筆畫庫完整+384爻完整"
    
    # 推送
    echo "🚀 推送到遠端..."
    git push origin main 2>/dev/null || git push origin master 2>/dev/null
    
    echo ""
    echo "✅ 部署完成！Render 將自動更新。"
    
else
    echo "❌ 未檢測到 Git 倉庫"
    echo ""
    echo "請先執行："
    echo "  git init"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/beidou-mingshu.git"
    echo ""
    echo "或者手動部署到 Render。"
fi

echo ""
echo "=========================================="
