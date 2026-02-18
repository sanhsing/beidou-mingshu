"""
部署模組 - A 部署
deploy/deploy.py | @星殼 | 2026-02-17
PYLIB: config, health_check

功能：
- 環境檢查
- 部署配置生成
- Render/Railway 部署
- Docker 構建
- 部署驗證
"""
import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DeployConfig:
    """部署配置"""
    
    # 支持的平台
    PLATFORMS = ['render', 'railway', 'docker', 'fly']
    
    # 必需文件
    REQUIRED_FILES = [
        'app.py', 'requirements.txt', 'config.py',
        'db_unified.py', 'bazi_base.py'
    ]
    
    # 必需環境變數
    REQUIRED_ENV_VARS = [
        'SECRET_KEY',
        'ECPAY_MERCHANT_ID',
        'ECPAY_HASH_KEY', 
        'ECPAY_HASH_IV'
    ]
    
    # 可選環境變數
    OPTIONAL_ENV_VARS = [
        'DATABASE_URL',
        'SMTP_HOST', 'SMTP_USER', 'SMTP_PASS',
        'SENTRY_DSN',
        'GA4_ID'
    ]


class DeployService:
    """部署服務"""
    
    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = project_root
        self.deploy_dir = project_root / "deploy"
        self.deploy_dir.mkdir(exist_ok=True)
    
    def check_prerequisites(self) -> Dict[str, Any]:
        """檢查部署前置條件"""
        print("[Deploy] 檢查前置條件...")
        
        checks = {
            'files': {},
            'env_vars': {},
            'ready': True
        }
        
        # 檢查必需文件
        for filename in DeployConfig.REQUIRED_FILES:
            filepath = self.project_root / filename
            exists = filepath.exists()
            checks['files'][filename] = exists
            if not exists:
                checks['ready'] = False
                print(f"  ❌ 缺少文件: {filename}")
            else:
                print(f"  ✅ {filename}")
        
        # 檢查環境變數
        for var in DeployConfig.REQUIRED_ENV_VARS:
            value = os.getenv(var)
            exists = bool(value)
            checks['env_vars'][var] = exists
            if not exists:
                checks['ready'] = False
                print(f"  ⚠️ 缺少環境變數: {var}")
        
        return checks
    
    def generate_render_config(self) -> Path:
        """生成 Render 配置"""
        config = {
            'services': [{
                'type': 'web',
                'name': 'beidou-mingshu',
                'env': 'python',
                'region': 'singapore',
                'plan': 'starter',
                'buildCommand': 'pip install -r requirements.txt',
                'startCommand': 'uvicorn app:app --host 0.0.0.0 --port $PORT',
                'healthCheckPath': '/api/health',
                'envVars': [
                    {'key': 'PYTHON_VERSION', 'value': '3.11.0'},
                    {'key': 'SECRET_KEY', 'generateValue': True},
                ]
            }]
        }
        
        # YAML 格式
        yaml_content = f"""# Render 部署配置
# 生成時間: {datetime.now().isoformat()}

services:
  - type: web
    name: beidou-mingshu
    env: python
    region: singapore
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /api/health
    envVars:
      - key: PYTHON_VERSION
        value: "3.11.0"
      - key: SECRET_KEY
        generateValue: true
      - key: ECPAY_SANDBOX
        value: "false"
"""
        
        output_path = self.project_root / "render.yaml"
        with open(output_path, 'w') as f:
            f.write(yaml_content)
        
        print(f"[Deploy] Render 配置已生成: {output_path}")
        return output_path
    
    def generate_railway_config(self) -> Path:
        """生成 Railway 配置"""
        config = {
            'build': {
                'builder': 'NIXPACKS'
            },
            'deploy': {
                'startCommand': 'uvicorn app:app --host 0.0.0.0 --port $PORT',
                'healthcheckPath': '/api/health',
                'healthcheckTimeout': 30
            }
        }
        
        output_path = self.project_root / "railway.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"[Deploy] Railway 配置已生成: {output_path}")
        return output_path
    
    def generate_dockerfile(self) -> Path:
        """生成 Dockerfile"""
        dockerfile = """# 北斗命數 SaaS Dockerfile
# 生成時間: {timestamp}

FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製代碼
COPY . .

# 環境變數
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
""".format(timestamp=datetime.now().isoformat())
        
        output_path = self.project_root / "Dockerfile"
        with open(output_path, 'w') as f:
            f.write(dockerfile)
        
        print(f"[Deploy] Dockerfile 已生成: {output_path}")
        return output_path
    
    def generate_docker_compose(self) -> Path:
        """生成 docker-compose.yml"""
        compose = """# 北斗命數 SaaS Docker Compose
# 生成時間: {timestamp}

version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${{SECRET_KEY}}
      - DATABASE_URL=${{DATABASE_URL:-sqlite:///./beidou_unified.db}}
      - ECPAY_MERCHANT_ID=${{ECPAY_MERCHANT_ID}}
      - ECPAY_HASH_KEY=${{ECPAY_HASH_KEY}}
      - ECPAY_HASH_IV=${{ECPAY_HASH_IV}}
      - ECPAY_SANDBOX=${{ECPAY_SANDBOX:-false}}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis (可選)
  # redis:
  #   image: redis:alpine
  #   restart: unless-stopped
""".format(timestamp=datetime.now().isoformat())
        
        output_path = self.project_root / "docker-compose.yml"
        with open(output_path, 'w') as f:
            f.write(compose)
        
        print(f"[Deploy] docker-compose.yml 已生成: {output_path}")
        return output_path
    
    def generate_env_template(self) -> Path:
        """生成環境變數模板"""
        template = """# 北斗命數 SaaS 環境變數
# 生成時間: {timestamp}
# 複製此文件為 .env 並填入實際值

# === 應用配置 ===
APP_ENV=production
DEBUG=false
SECRET_KEY=your-super-secret-key-change-this

# === 數據庫 ===
DATABASE_URL=sqlite:///./beidou_unified.db

# === 綠界支付 ===
ECPAY_MERCHANT_ID=your-merchant-id
ECPAY_HASH_KEY=your-hash-key
ECPAY_HASH_IV=your-hash-iv
ECPAY_SANDBOX=false

# === Email (可選) ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
FROM_EMAIL=noreply@beidou-mingshu.com

# === 監控 (可選) ===
SENTRY_DSN=
GA4_ID=

# === 網站 ===
SITE_URL=https://your-domain.com
""".format(timestamp=datetime.now().isoformat())
        
        output_path = self.project_root / ".env.template"
        with open(output_path, 'w') as f:
            f.write(template)
        
        print(f"[Deploy] .env.template 已生成: {output_path}")
        return output_path
    
    def generate_deploy_guide(self) -> Path:
        """生成部署指南"""
        guide = """# 北斗命數 SaaS 部署指南

> 生成時間: {timestamp}

---

## 📋 部署前檢查清單

- [ ] 環境變數已設定
- [ ] 數據庫已初始化
- [ ] 支付帳號已配置
- [ ] 域名已準備

---

## 🚀 部署方式

### 方式 1: Render (推薦)

1. Fork 專案到 GitHub
2. 登入 [Render](https://render.com)
3. 新建 Web Service
4. 連接 GitHub 倉庫
5. 設定環境變數
6. 部署

```bash
# render.yaml 已準備好
```

### 方式 2: Railway

1. 登入 [Railway](https://railway.app)
2. 新建專案
3. 連接 GitHub 倉庫
4. 設定環境變數
5. 部署

```bash
# railway.json 已準備好
```

### 方式 3: Docker

```bash
# 構建鏡像
docker build -t beidou-mingshu .

# 運行容器
docker run -d -p 8000:8000 --env-file .env beidou-mingshu

# 或使用 docker-compose
docker-compose up -d
```

---

## 🔧 環境變數設定

| 變數 | 必需 | 說明 |
|------|:----:|------|
| SECRET_KEY | ✅ | 應用密鑰 |
| ECPAY_MERCHANT_ID | ✅ | 綠界商店代號 |
| ECPAY_HASH_KEY | ✅ | 綠界 HashKey |
| ECPAY_HASH_IV | ✅ | 綠界 HashIV |
| DATABASE_URL | ⬜ | 數據庫連接 |
| SMTP_HOST | ⬜ | 郵件伺服器 |
| SENTRY_DSN | ⬜ | 錯誤監控 |

---

## ✅ 部署驗證

部署完成後，訪問以下端點確認服務正常：

1. 健康檢查: `GET /api/health`
2. 首頁: `GET /`
3. 免費試算: `GET /free`

```bash
# 健康檢查
curl https://your-domain.com/api/health

# 預期返回
{{"status": "ok", "version": "1.0.0"}}
```

---

## 📞 支援

如遇問題，請聯繫：service@beidou-mingshu.com

""".format(timestamp=datetime.now().isoformat())
        
        output_path = self.deploy_dir / "DEPLOY_GUIDE.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print(f"[Deploy] 部署指南已生成: {output_path}")
        return output_path
    
    def prepare_all(self) -> Dict[str, Path]:
        """準備所有部署配置"""
        print("\n" + "=" * 60)
        print("  北斗命數 SaaS - 部署準備")
        print("=" * 60)
        
        # 前置檢查
        prereq = self.check_prerequisites()
        
        if not prereq['ready']:
            print("\n⚠️ 前置條件未滿足，請先修復上述問題")
        
        print("\n📦 生成部署配置...")
        
        outputs = {
            'render': self.generate_render_config(),
            'railway': self.generate_railway_config(),
            'dockerfile': self.generate_dockerfile(),
            'docker_compose': self.generate_docker_compose(),
            'env_template': self.generate_env_template(),
            'guide': self.generate_deploy_guide()
        }
        
        print("\n✅ 部署配置準備完成")
        print("\n生成的文件:")
        for name, path in outputs.items():
            print(f"  - {path.name}")
        
        return outputs


def notify_telegram(message: str) -> bool:
    """發送 Telegram 通知"""
    import urllib.request
    import urllib.parse
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8080151081:AAEV7amkwA7l2VEKteah7r2kyMEcWhI8NUc')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '5965951659')
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }).encode()
        
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"[Deploy] Telegram 通知失敗: {e}")
        return False


def run_deploy(notify: bool = True) -> Dict[str, Any]:
    """執行部署準備"""
    ds = DeployService()
    outputs = ds.prepare_all()
    
    if notify:
        msg = """🚀 *北斗命數 - 部署配置已準備*

已生成:
• render.yaml
• railway.json  
• Dockerfile
• docker-compose.yml
• .env.template
• DEPLOY_GUIDE.md

下一步: 選擇平台部署

@星殼"""
        notify_telegram(msg)
    
    return {
        'success': True,
        'outputs': {k: str(v) for k, v in outputs.items()}
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='北斗命數部署工具')
    parser.add_argument('--no-notify', action='store_true', help='不發送通知')
    parser.add_argument('--check', action='store_true', help='只檢查前置條件')
    
    args = parser.parse_args()
    
    if args.check:
        ds = DeployService()
        ds.check_prerequisites()
    else:
        result = run_deploy(notify=not args.no_notify)
        print(f"\n結果: {result}")
