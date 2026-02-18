# ═══════════════════════════════════════════════════════════════════
# 北斗命數系統 Dockerfile
# 版本：v1.0.0
# XTF Task Chain: C3
# ═══════════════════════════════════════════════════════════════════

FROM python:3.11-slim

LABEL maintainer="BeiDou MingShu"
LABEL version="1.0.0"
LABEL description="北斗命數命理分析系統"

# 設置工作目錄
WORKDIR /app

# 設置環境變數
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Taipei
ENV ENV=production
ENV DEBUG=false

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式
COPY . .

# 創建數據目錄
RUN mkdir -p /app/data /app/logs

# 創建非 root 用戶
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 啟動命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
