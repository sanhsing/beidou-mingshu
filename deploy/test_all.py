"""
全功能測試模組 - B 測試
deploy/test_all.py | @理樞 | 2026-02-17
PYLIB: health_check, monitoring, config

功能：
- 依賴檢查
- 模組載入測試
- API 端點測試
- 數據庫連接測試
- 支付模組測試
- 生成測試報告
"""
import os
import sys
import json
import time
import sqlite3
import importlib
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# 添加項目根目錄到路徑
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# === 測試配置 ===
REQUIRED_MODULES = [
    'fastapi', 'uvicorn', 'pydantic', 'sqlalchemy',
    'reportlab', 'python-jose', 'passlib', 'httpx',
    'python-multipart', 'loguru'
]

CORE_PY_MODULES = [
    'app', 'config', 'db_unified', 'bazi_base', 'bazi_free',
    'payment_service', 'email_service', 'membership_service',
    'health_check', 'monitoring'
]

API_ENDPOINTS = [
    ('GET', '/api/health', 200),
    ('GET', '/api/health/live', 200),
]


class TestRunner:
    """測試執行器"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def add_result(self, category: str, name: str, passed: bool, 
                   message: str = '', duration: float = 0):
        """添加測試結果"""
        self.results.append({
            'category': category,
            'name': name,
            'passed': passed,
            'message': message,
            'duration': duration
        })
    
    def run_test(self, category: str, name: str, test_func):
        """執行單個測試"""
        start = time.time()
        try:
            result = test_func()
            duration = time.time() - start
            
            if isinstance(result, tuple):
                passed, message = result
            else:
                passed = bool(result)
                message = ''
            
            self.add_result(category, name, passed, message, duration)
            status = "✅" if passed else "❌"
            print(f"  {status} {name} ({duration:.3f}s)")
            return passed
            
        except Exception as e:
            duration = time.time() - start
            self.add_result(category, name, False, str(e), duration)
            print(f"  ❌ {name}: {e}")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """獲取測試摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        by_category = {}
        for r in self.results:
            cat = r['category']
            if cat not in by_category:
                by_category[cat] = {'total': 0, 'passed': 0}
            by_category[cat]['total'] += 1
            if r['passed']:
                by_category[cat]['passed'] += 1
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / total * 100) if total > 0 else 0,
            'duration': (self.end_time - self.start_time) if self.end_time else 0,
            'by_category': by_category,
            'results': self.results
        }


def test_dependencies() -> List[Tuple[str, bool, str]]:
    """測試 Python 依賴"""
    results = []
    
    dep_map = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'pydantic': 'pydantic',
        'sqlalchemy': 'sqlalchemy',
        'reportlab': 'reportlab',
        'python-jose': 'jose',
        'passlib': 'passlib',
        'httpx': 'httpx',
        'python-multipart': 'multipart',
        'loguru': 'loguru',
        'python-dotenv': 'dotenv'
    }
    
    for pkg, module in dep_map.items():
        try:
            importlib.import_module(module)
            results.append((pkg, True, ''))
        except ImportError as e:
            results.append((pkg, False, str(e)))
    
    return results


def test_module_import(module_name: str) -> Tuple[bool, str]:
    """測試模組導入"""
    try:
        module = importlib.import_module(module_name)
        return True, f"版本: {getattr(module, '__version__', 'N/A')}"
    except Exception as e:
        return False, str(e)


def test_database() -> Tuple[bool, str]:
    """測試數據庫連接"""
    db_path = PROJECT_ROOT / "beidou_unified.db"
    
    if not db_path.exists():
        return False, "數據庫文件不存在"
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 檢查表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return True, f"表數量: {len(tables)}"
    except Exception as e:
        return False, str(e)


def test_config() -> Tuple[bool, str]:
    """測試配置載入"""
    try:
        from config import settings
        
        required = ['SECRET_KEY', 'DATABASE_URL']
        missing = [k for k in required if not getattr(settings, k, None)]
        
        if missing:
            return False, f"缺少配置: {missing}"
        
        return True, "配置完整"
    except Exception as e:
        return False, str(e)


def test_payment_service() -> Tuple[bool, str]:
    """測試支付服務"""
    try:
        from payment_service import PaymentService, PaymentProvider
        
        ps = PaymentService(provider=PaymentProvider.ECPAY)
        plans = ps.get_plans()
        
        return True, f"方案數: {len(plans)}"
    except Exception as e:
        return False, str(e)


def test_bazi_engine() -> Tuple[bool, str]:
    """測試八字引擎"""
    try:
        from bazi_free import free_bazi_analyze
        
        result = free_bazi_analyze(1990, 5, 15, 14)
        
        if 'bazi' in result and 'day_master' in result:
            return True, f"日主: {result['day_master']}"
        return False, "返回格式錯誤"
    except Exception as e:
        return False, str(e)


def test_email_service() -> Tuple[bool, str]:
    """測試郵件服務"""
    try:
        from email_service import EmailService
        
        es = EmailService()
        return True, f"SMTP: {es.smtp_host}"
    except Exception as e:
        return False, str(e)


def test_membership_service() -> Tuple[bool, str]:
    """測試會員服務"""
    try:
        from membership_service import MembershipService, MEMBERSHIP_PLANS
        
        ms = MembershipService()
        return True, f"方案數: {len(MEMBERSHIP_PLANS)}"
    except Exception as e:
        return False, str(e)


def test_app_routes() -> Tuple[bool, str]:
    """測試應用路由"""
    try:
        from app import app
        
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        
        required = ['/', '/login', '/register', '/bazi', '/pricing']
        missing = [r for r in required if r not in routes]
        
        if missing:
            return False, f"缺少路由: {missing}"
        
        return True, f"路由數: {len(routes)}"
    except Exception as e:
        return False, str(e)


def run_all_tests() -> Dict[str, Any]:
    """執行所有測試"""
    runner = TestRunner()
    runner.start_time = time.time()
    
    print("\n" + "=" * 60)
    print("  北斗命數 SaaS - 全功能測試")
    print("=" * 60)
    
    # 1. 依賴測試
    print("\n📦 依賴檢查")
    dep_results = test_dependencies()
    for pkg, passed, msg in dep_results:
        runner.add_result('dependencies', pkg, passed, msg)
        status = "✅" if passed else "❌"
        print(f"  {status} {pkg}")
    
    # 2. 核心模組測試
    print("\n🔧 核心模組")
    for module in CORE_PY_MODULES:
        runner.run_test('modules', module, lambda m=module: test_module_import(m))
    
    # 3. 數據庫測試
    print("\n💾 數據庫")
    runner.run_test('database', 'SQLite 連接', test_database)
    
    # 4. 配置測試
    print("\n⚙️ 配置")
    runner.run_test('config', '環境配置', test_config)
    
    # 5. 服務測試
    print("\n🔌 服務")
    runner.run_test('services', '支付服務', test_payment_service)
    runner.run_test('services', '八字引擎', test_bazi_engine)
    runner.run_test('services', '郵件服務', test_email_service)
    runner.run_test('services', '會員服務', test_membership_service)
    
    # 6. 路由測試
    print("\n🌐 路由")
    runner.run_test('routes', '應用路由', test_app_routes)
    
    runner.end_time = time.time()
    
    # 輸出摘要
    summary = runner.get_summary()
    
    print("\n" + "=" * 60)
    print("  測試結果")
    print("=" * 60)
    print(f"  總計: {summary['total']} 項")
    print(f"  通過: {summary['passed']} ✅")
    print(f"  失敗: {summary['failed']} ❌")
    print(f"  通過率: {summary['pass_rate']:.1f}%")
    print(f"  耗時: {summary['duration']:.2f}s")
    
    return summary


def generate_report(summary: Dict[str, Any], output_path: Path = None) -> Path:
    """生成測試報告"""
    output_path = output_path or PROJECT_ROOT / "deploy" / "test_report.json"
    
    report = {
        'title': '北斗命數 SaaS 測試報告',
        'generated': datetime.now().isoformat(),
        'summary': {
            'total': summary['total'],
            'passed': summary['passed'],
            'failed': summary['failed'],
            'pass_rate': f"{summary['pass_rate']:.1f}%",
            'duration': f"{summary['duration']:.2f}s"
        },
        'by_category': summary['by_category'],
        'details': summary['results']
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📝 報告已生成: {output_path}")
    return output_path


def notify_telegram(summary: Dict[str, Any]) -> bool:
    """發送 Telegram 通知"""
    import urllib.request
    import urllib.parse
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8080151081:AAEV7amkwA7l2VEKteah7r2kyMEcWhI8NUc')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '5965951659')
    
    status = "✅ 通過" if summary['failed'] == 0 else "⚠️ 有失敗"
    
    text = f"""🧪 *北斗命數 - 測試報告*

{status}

總計: {summary['total']} 項
通過: {summary['passed']} ✅
失敗: {summary['failed']} ❌
通過率: {summary['pass_rate']:.1f}%
耗時: {summary['duration']:.2f}s

@理樞"""
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }).encode()
        
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"[Test] Telegram 通知失敗: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='北斗命數測試工具')
    parser.add_argument('--report', action='store_true', help='生成報告')
    parser.add_argument('--notify', action='store_true', help='發送通知')
    
    args = parser.parse_args()
    
    summary = run_all_tests()
    
    if args.report:
        generate_report(summary)
    
    if args.notify:
        notify_telegram(summary)
    
    # 退出碼
    sys.exit(0 if summary['failed'] == 0 else 1)
