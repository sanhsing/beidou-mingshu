# 北斗命數 Docker 映像
FROM python:3.11-slim

LABEL maintainer="北斗七星文創 <beidou@example.com>"
LABEL version="2.0.0"

# 設置工作目錄
WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用
COPY . .

# 環境變量
ENV FLASK_ENV=production
ENV MINGSHU_PORT=5000
ENV MINGSHU_HOST=0.0.0.0

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${MINGSHU_PORT}/health || exit 1

# 暴露端口
EXPOSE ${MINGSHU_PORT}

# 啟動命令
CMD ["python", "mingshu_api_unified_v2.py", "--serve", "5000"]
