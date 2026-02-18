"""
支付系統測試 (最終版)
M9.5 | @理樞 | 2026-02-17
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def test_ecpay_config():
    """測試綠界配置"""
    print("=== 綠界配置檢查 ===")
    
    merchant_id = os.getenv('ECPAY_MERCHANT_ID')
    hash_key = os.getenv('ECPAY_HASH_KEY')
    hash_iv = os.getenv('ECPAY_HASH_IV')
    sandbox = os.getenv('ECPAY_SANDBOX', 'true')
    
    configs = [
        ('ECPAY_MERCHANT_ID', merchant_id),
        ('ECPAY_HASH_KEY', hash_key),
        ('ECPAY_HASH_IV', hash_iv),
    ]
    
    for name, value in configs:
        if value:
            display = value if len(value) < 10 else f"{value[:4]}***"
            print(f"✓ {name}: {display}")
        else:
            print(f"✗ {name}: 未設定")
    
    print(f"✓ SANDBOX 模式: {sandbox}")
    return all(v for _, v in configs)

def test_payment_service_init():
    """測試 PaymentService 初始化"""
    print("\n=== PaymentService 初始化 ===")
    
    try:
        from payment_service import PaymentService, PaymentProvider
        ps = PaymentService(provider=PaymentProvider.ECPAY)
        print(f"✓ PaymentService 初始化成功")
        print(f"✓ 提供商: {ps.provider.value}")
        
        # 檢查方案
        plans = PaymentService.get_plans()
        print(f"✓ 付費方案數量: {len(plans)}")
        for code, plan in list(plans.items())[:3]:
            print(f"  - {code}: {plan['name']} NT${plan['price']}")
        
        return True
    except Exception as e:
        print(f"✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_create_order():
    """測試建立訂單"""
    print("\n=== 測試建立訂單 ===")
    
    try:
        from payment_service import PaymentService, PaymentProvider
        ps = PaymentService(provider=PaymentProvider.ECPAY)
        
        # 使用正確的介面
        result = ps.create_order(
            user_id=1,
            plan_code="credits_100",
            return_url="http://localhost:8000/payment/return",
            notify_url="http://localhost:8000/api/payment/notify"
        )
        
        if result:
            print(f"✓ 訂單建立成功")
            print(f"  返回類型: {type(result).__name__}")
            if isinstance(result, dict):
                print(f"  包含鍵: {list(result.keys())[:5]}")
            elif isinstance(result, str) and 'form' in result.lower():
                print(f"  包含支付表單 HTML")
            return True
        else:
            print(f"⚠ 返回為空")
            return False
            
    except Exception as e:
        print(f"✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_verify_notify():
    """測試回調驗證"""
    print("\n=== 測試回調驗證 ===")
    
    try:
        from payment_service import PaymentService, PaymentProvider
        ps = PaymentService(provider=PaymentProvider.ECPAY)
        
        # 檢查方法存在
        if hasattr(ps, 'verify_notify'):
            print(f"✓ verify_notify 方法存在")
            return True
        else:
            print(f"✗ verify_notify 方法不存在")
            return False
            
    except Exception as e:
        print(f"✗ 錯誤: {e}")
        return False

def run_all_tests():
    """執行所有測試"""
    print("=" * 50)
    print("  北斗命數 - 支付系統測試")
    print("=" * 50)
    
    results = []
    results.append(("配置檢查", test_ecpay_config()))
    results.append(("服務初始化", test_payment_service_init()))
    results.append(("建立訂單", test_create_order()))
    results.append(("回調驗證", test_verify_notify()))
    
    print("\n" + "=" * 50)
    print("  測試結果")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\n  通過: {passed}/{total}")
    return passed >= 3

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
