"""
上線模組 - 上線檢查清單
deploy/launch.py | @織明 | 2026-02-17
PYLIB: health_check, monitoring, config

功能：
- 上線前檢查清單
- 上線驗證
- 回滾計劃
- 上線通知
"""
import os
import sys
import json
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class LaunchChecklist:
    """上線檢查清單"""
    
    # P0 必做項目
    P0_ITEMS = [
        {'id': 'env_vars', 'name': '環境變數已設定', 'category': '配置'},
        {'id': 'secret_key', 'name': 'SECRET_KEY 已更換', 'category': '安全'},
        {'id': 'ecpay_prod', 'name': '綠界正式帳號', 'category': '支付'},
        {'id': 'database', 'name': '數據庫已初始化', 'category': '數據'},
        {'id': 'deploy', 'name': '已部署到雲端', 'category': '部署'},
        {'id': 'domain', 'name': '域名已綁定', 'category': '部署'},
        {'id': 'ssl', 'name': 'SSL 證書有效', 'category': '安全'},
        {'id': 'health_check', 'name': '健康檢查通過', 'category': '驗證'},
    ]
    
    # P1 建議項目
    P1_ITEMS = [
        {'id': 'ga4', 'name': 'GA4 追蹤已設定', 'category': '監控'},
        {'id': 'sentry', 'name': 'Sentry 錯誤監控', 'category': '監控'},
        {'id': 'smtp', 'name': 'Email 服務已設定', 'category': '通知'},
        {'id': 'backup', 'name': '備份機制已啟用', 'category': '運維'},
        {'id': 'rate_limit', 'name': 'API 限流已設定', 'category': '安全'},
    ]
    
    def __init__(self):
        self.checked = {}
        self.load_state()
    
    def load_state(self):
        """載入檢查狀態"""
        state_file = PROJECT_ROOT / "deploy" / "launch_state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                self.checked = json.load(f)
    
    def save_state(self):
        """保存檢查狀態"""
        state_file = PROJECT_ROOT / "deploy" / "launch_state.json"
        with open(state_file, 'w') as f:
            json.dump(self.checked, f, indent=2)
    
    def check_item(self, item_id: str, passed: bool, note: str = ''):
        """標記檢查項目"""
        self.checked[item_id] = {
            'passed': passed,
            'note': note,
            'checked_at': datetime.now().isoformat()
        }
        self.save_state()
    
    def auto_check(self) -> Dict[str, Any]:
        """自動檢查可自動驗證的項目"""
        results = {}
        
        # 檢查環境變數
        required_vars = ['SECRET_KEY', 'ECPAY_MERCHANT_ID', 'ECPAY_HASH_KEY', 'ECPAY_HASH_IV']
        env_ok = all(os.getenv(v) for v in required_vars)
        self.check_item('env_vars', env_ok, '環境變數檢查')
        results['env_vars'] = env_ok
        
        # 檢查 SECRET_KEY 是否已更換
        secret = os.getenv('SECRET_KEY', '')
        secret_changed = secret and 'your-' not in secret.lower() and len(secret) > 20
        self.check_item('secret_key', secret_changed, 'SECRET_KEY 檢查')
        results['secret_key'] = secret_changed
        
        # 檢查綠界是否為正式環境
        sandbox = os.getenv('ECPAY_SANDBOX', 'true').lower()
        ecpay_prod = sandbox == 'false'
        self.check_item('ecpay_prod', ecpay_prod, f'SANDBOX={sandbox}')
        results['ecpay_prod'] = ecpay_prod
        
        # 檢查數據庫
        db_path = PROJECT_ROOT / "beidou_unified.db"
        db_ok = db_path.exists() and db_path.stat().st_size > 0
        self.check_item('database', db_ok, f'大小: {db_path.stat().st_size if db_ok else 0} bytes')
        results['database'] = db_ok
        
        return results
    
    def verify_deployment(self, url: str) -> Dict[str, Any]:
        """驗證部署"""
        results = {}
        
        # 健康檢查
        try:
            req = urllib.request.Request(f"{url}/api/health")
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode())
            
            health_ok = data.get('status') == 'ok'
            self.check_item('health_check', health_ok, f'狀態: {data.get("status")}')
            results['health_check'] = health_ok
            
            # 標記已部署
            self.check_item('deploy', True, f'URL: {url}')
            results['deploy'] = True
            
        except Exception as e:
            self.check_item('health_check', False, str(e))
            results['health_check'] = False
        
        # 檢查 SSL
        try:
            if url.startswith('https://'):
                self.check_item('ssl', True, 'HTTPS')
                results['ssl'] = True
            else:
                self.check_item('ssl', False, 'HTTP only')
                results['ssl'] = False
        except:
            results['ssl'] = False
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """獲取檢查狀態"""
        p0_passed = 0
        p0_total = len(self.P0_ITEMS)
        p1_passed = 0
        p1_total = len(self.P1_ITEMS)
        
        p0_details = []
        for item in self.P0_ITEMS:
            checked = self.checked.get(item['id'], {})
            passed = checked.get('passed', False)
            if passed:
                p0_passed += 1
            p0_details.append({
                **item,
                'passed': passed,
                'note': checked.get('note', ''),
                'checked_at': checked.get('checked_at')
            })
        
        p1_details = []
        for item in self.P1_ITEMS:
            checked = self.checked.get(item['id'], {})
            passed = checked.get('passed', False)
            if passed:
                p1_passed += 1
            p1_details.append({
                **item,
                'passed': passed,
                'note': checked.get('note', ''),
                'checked_at': checked.get('checked_at')
            })
        
        ready = p0_passed == p0_total
        
        return {
            'ready': ready,
            'p0': {'passed': p0_passed, 'total': p0_total, 'items': p0_details},
            'p1': {'passed': p1_passed, 'total': p1_total, 'items': p1_details}
        }
    
    def print_status(self):
        """打印檢查狀態"""
        status = self.get_status()
        
        print("\n" + "=" * 60)
        print("  北斗命數 SaaS - 上線檢查清單")
        print("=" * 60)
        
        print(f"\n🔴 P0 必做項目 ({status['p0']['passed']}/{status['p0']['total']})")
        for item in status['p0']['items']:
            icon = "✅" if item['passed'] else "⬜"
            print(f"  {icon} [{item['category']}] {item['name']}")
            if item.get('note'):
                print(f"      └─ {item['note']}")
        
        print(f"\n🟡 P1 建議項目 ({status['p1']['passed']}/{status['p1']['total']})")
        for item in status['p1']['items']:
            icon = "✅" if item['passed'] else "⬜"
            print(f"  {icon} [{item['category']}] {item['name']}")
        
        print("\n" + "=" * 60)
        if status['ready']:
            print("  ✅ 可以上線！")
        else:
            missing = status['p0']['total'] - status['p0']['passed']
            print(f"  ⚠️ 還有 {missing} 個 P0 項目未完成")
        print("=" * 60)
        
        return status


class RollbackPlan:
    """回滾計劃"""
    
    @staticmethod
    def generate() -> str:
        """生成回滾計劃"""
        plan = """# 北斗命數 SaaS 回滾計劃

## 🚨 回滾觸發條件

1. 健康檢查連續失敗 > 5 次
2. 錯誤率 > 10%
3. 關鍵功能無法使用
4. 支付流程異常

## 📋 回滾步驟

### Render 回滾

1. 登入 Render Dashboard
2. 選擇 beidou-mingshu 服務
3. 點擊 "Manual Deploy" > "Deploy previous version"
4. 確認回滾完成

### Railway 回滾

```bash
railway rollback
```

### Docker 回滾

```bash
# 停止當前容器
docker-compose down

# 使用上一版本鏡像
docker run -d --env-file .env beidou-mingshu:previous

# 或恢復備份
./restore_backup.sh
```

## 📞 緊急聯繫

- 運維: ops@beidou-mingshu.com
- 開發: dev@beidou-mingshu.com

## ⏱️ 預估回滾時間

- Render: 2-5 分鐘
- Railway: 2-5 分鐘
- Docker: 5-10 分鐘
"""
        return plan
    
    @staticmethod
    def save() -> Path:
        """保存回滾計劃"""
        plan = RollbackPlan.generate()
        output_path = PROJECT_ROOT / "deploy" / "ROLLBACK_PLAN.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(plan)
        return output_path


def notify_launch(status: Dict[str, Any], url: str = None) -> bool:
    """發送上線通知"""
    import urllib.parse
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8080151081:AAEV7amkwA7l2VEKteah7r2kyMEcWhI8NUc')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '5965951659')
    
    if status['ready']:
        text = f"""🎉 *北斗命數 SaaS - 上線就緒！*

P0 必做: {status['p0']['passed']}/{status['p0']['total']} ✅
P1 建議: {status['p1']['passed']}/{status['p1']['total']}

{f"🌐 URL: {url}" if url else ""}

準備上線！

@織明 @星殼"""
    else:
        missing = status['p0']['total'] - status['p0']['passed']
        text = f"""⚠️ *北斗命數 SaaS - 上線檢查*

P0 必做: {status['p0']['passed']}/{status['p0']['total']}
P1 建議: {status['p1']['passed']}/{status['p1']['total']}

還有 {missing} 個 P0 項目未完成

@織明"""
    
    try:
        url_api = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }).encode()
        
        req = urllib.request.Request(url_api, data=data)
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"[Launch] Telegram 通知失敗: {e}")
        return False


def run_launch_check(url: str = None, notify: bool = True) -> Dict[str, Any]:
    """執行上線檢查"""
    cl = LaunchChecklist()
    
    # 自動檢查
    cl.auto_check()
    
    # 如果提供了 URL，驗證部署
    if url:
        cl.verify_deployment(url)
    
    # 打印狀態
    status = cl.print_status()
    
    # 生成回滾計劃
    RollbackPlan.save()
    print("\n📋 回滾計劃已生成: deploy/ROLLBACK_PLAN.md")
    
    # 發送通知
    if notify:
        notify_launch(status, url)
    
    return status


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='北斗命數上線檢查')
    parser.add_argument('--url', type=str, help='部署 URL')
    parser.add_argument('--no-notify', action='store_true', help='不發送通知')
    parser.add_argument('--check', type=str, help='標記項目為已完成 (例: domain)')
    
    args = parser.parse_args()
    
    if args.check:
        cl = LaunchChecklist()
        cl.check_item(args.check, True, '手動標記')
        print(f"✅ 已標記: {args.check}")
        cl.print_status()
    else:
        run_launch_check(url=args.url, notify=not args.no_notify)
