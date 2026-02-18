"""
購買頁模組
checkout.py | @璃語 | 2026-02-17
PYLIB: payment_service, db_unified, auth_jwt

功能：
- 商品選擇頁
- 購買確認頁
- 支付跳轉
"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import json

router = APIRouter(prefix="/checkout", tags=["checkout"])

# === 商品定義 (對照規格書) ===
PRODUCTS = {
    # Tier 1-4 套餐
    'tier1_basic': {
        'name': '基礎命盤',
        'price': 299,
        'credits': 0,
        'type': 'package',
        'features': ['八字四柱排盤', '五行分析', '日主性格', '十神分析', 'PDF報告(12頁)'],
        'icon': '🌟'
    },
    'tier2_complete': {
        'name': '完整命理',
        'price': 599,
        'credits': 0,
        'type': 'package',
        'features': ['包含基礎命盤', '紫微斗數', '十年大運', '流年運勢', '事業感情建議', 'PDF報告(30頁)'],
        'icon': '⭐',
        'popular': True
    },
    'tier3_premium': {
        'name': '尊榮會員',
        'price': 1999,
        'credits': 0,
        'type': 'subscription',
        'duration': 365,
        'features': ['完整命理全部', '每月運勢更新', '3次擇日服務', '1次命名分析', '無限合婚配對', '專屬客服'],
        'icon': '💎'
    },
    'tier4_family': {
        'name': '家族方案',
        'price': 4999,
        'credits': 0,
        'type': 'subscription',
        'duration': 365,
        'max_members': 5,
        'features': ['尊榮會員×5人', '家族關係分析', '12次擇日', '5次命名', '優先客服'],
        'icon': '👑'
    },
    # 點數包
    'credits_100': {
        'name': '100 點數',
        'price': 99,
        'credits': 100,
        'type': 'credits',
        'icon': '💰'
    },
    'credits_300': {
        'name': '300 點數',
        'price': 249,
        'credits': 300,
        'type': 'credits',
        'discount': '省16%',
        'icon': '💰'
    },
    'credits_500': {
        'name': '500 點數',
        'price': 399,
        'credits': 500,
        'type': 'credits',
        'discount': '省20%',
        'popular': True,
        'icon': '💰'
    },
    'credits_1000': {
        'name': '1000 點數',
        'price': 699,
        'credits': 1000,
        'type': 'credits',
        'discount': '省30%',
        'icon': '💰'
    },
}

CHECKOUT_SELECT_HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>選擇商品 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .product-card {{ transition: all 0.3s; cursor: pointer; }}
        .product-card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.15); }}
        .product-card.selected {{ border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.3); }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <a href="/dashboard" class="hover:text-purple-200">← 返回</a>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-8">
        <h1 class="text-3xl font-bold text-gray-800 text-center mb-2">選擇商品</h1>
        <p class="text-gray-500 text-center mb-8">選擇適合您的方案或點數包</p>

        <form action="/checkout/confirm" method="post" id="checkoutForm">
            <!-- 套餐區 -->
            <h2 class="text-xl font-bold text-gray-700 mb-4">📦 套餐方案</h2>
            <div class="grid md:grid-cols-2 gap-4 mb-8">
                {package_cards}
            </div>

            <!-- 點數包區 -->
            <h2 class="text-xl font-bold text-gray-700 mb-4">💰 點數儲值</h2>
            <div class="grid md:grid-cols-4 gap-4 mb-8">
                {credits_cards}
            </div>

            <input type="hidden" name="product_id" id="selectedProduct" value="">
            
            <div class="text-center">
                <button type="submit" id="submitBtn" disabled
                        class="gradient-bg text-white px-12 py-4 rounded-xl text-xl font-bold 
                               disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 transition">
                    前往結帳 →
                </button>
                <p class="text-gray-400 text-sm mt-4" id="selectedInfo">請選擇一個商品</p>
            </div>
        </form>
    </main>

    <script>
        const products = {products_json};
        let selected = null;
        
        document.querySelectorAll('.product-card').forEach(card => {{
            card.addEventListener('click', function() {{
                // 移除其他選中
                document.querySelectorAll('.product-card').forEach(c => c.classList.remove('selected'));
                // 選中當前
                this.classList.add('selected');
                selected = this.dataset.productId;
                document.getElementById('selectedProduct').value = selected;
                document.getElementById('submitBtn').disabled = false;
                
                const product = products[selected];
                document.getElementById('selectedInfo').textContent = 
                    `已選擇: ${{product.name}} - NT$${{product.price}}`;
            }});
        }});
        
        document.getElementById('checkoutForm').addEventListener('submit', function(e) {{
            if (!selected) {{
                e.preventDefault();
                alert('請先選擇商品');
            }}
        }});
    </script>
</body>
</html>'''

CHECKOUT_CONFIRM_HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>確認訂單 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>.gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}</style>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <a href="/checkout" class="hover:text-purple-200">← 返回選擇</a>
        </div>
    </nav>

    <main class="max-w-lg mx-auto px-6 py-12">
        <h1 class="text-3xl font-bold text-gray-800 text-center mb-8">確認訂單</h1>

        <div class="bg-white rounded-2xl shadow-xl p-8 mb-6">
            <!-- 商品資訊 -->
            <div class="flex items-center gap-4 mb-6 pb-6 border-b">
                <span class="text-5xl">{icon}</span>
                <div>
                    <h2 class="text-xl font-bold text-gray-800">{name}</h2>
                    <p class="text-gray-500">{type_label}</p>
                </div>
            </div>

            <!-- 功能列表 -->
            <div class="mb-6">
                <h3 class="font-bold text-gray-700 mb-2">包含內容：</h3>
                <ul class="space-y-1">
                    {features_html}
                </ul>
            </div>

            <!-- 價格 -->
            <div class="flex justify-between items-center py-4 border-t border-b">
                <span class="text-gray-600">小計</span>
                <span class="text-2xl font-bold text-purple-600">NT${price}</span>
            </div>

            <!-- 付款方式 -->
            <div class="mt-6">
                <h3 class="font-bold text-gray-700 mb-3">付款方式</h3>
                <div class="space-y-2">
                    <label class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                        <input type="radio" name="payment_method" value="credit" checked class="text-purple-600">
                        <span>💳 信用卡</span>
                    </label>
                    <label class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                        <input type="radio" name="payment_method" value="atm" class="text-purple-600">
                        <span>🏧 ATM 轉帳</span>
                    </label>
                    <label class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                        <input type="radio" name="payment_method" value="cvs" class="text-purple-600">
                        <span>🏪 超商代碼</span>
                    </label>
                </div>
            </div>
        </div>

        <!-- 結帳按鈕 -->
        <form action="/checkout/pay" method="post">
            <input type="hidden" name="product_id" value="{product_id}">
            <button type="submit" class="w-full gradient-bg text-white py-4 rounded-xl text-xl font-bold hover:opacity-90">
                確認付款 NT${price}
            </button>
        </form>

        <p class="text-center text-gray-400 text-sm mt-4">
            點擊付款即表示同意 <a href="/legal/terms" class="text-purple-600 hover:underline">服務條款</a>
        </p>
    </main>
</body>
</html>'''


def render_package_card(pid: str, product: dict) -> str:
    """渲染套餐卡片"""
    popular = '<div class="absolute -top-2 right-4 bg-purple-600 text-white text-xs px-2 py-1 rounded-full">最受歡迎</div>' if product.get('popular') else ''
    
    features = ''.join([f'<li class="text-sm text-gray-600">✓ {f}</li>' for f in product.get('features', [])[:4]])
    
    return f'''
    <div class="product-card bg-white rounded-xl p-6 border-2 border-gray-200 relative" data-product-id="{pid}">
        {popular}
        <div class="flex items-center gap-3 mb-4">
            <span class="text-3xl">{product['icon']}</span>
            <div>
                <h3 class="font-bold text-gray-800">{product['name']}</h3>
                <p class="text-2xl font-bold text-purple-600">NT${product['price']}</p>
            </div>
        </div>
        <ul class="space-y-1">{features}</ul>
    </div>
    '''


def render_credits_card(pid: str, product: dict) -> str:
    """渲染點數卡片"""
    discount = f'<span class="text-green-500 text-xs">{product["discount"]}</span>' if product.get('discount') else ''
    popular = 'border-purple-400' if product.get('popular') else 'border-gray-200'
    
    return f'''
    <div class="product-card bg-white rounded-xl p-4 border-2 {popular} text-center" data-product-id="{pid}">
        <div class="text-2xl font-bold text-purple-600">{product['credits']} 點</div>
        <div class="text-gray-600">NT${product['price']}</div>
        {discount}
    </div>
    '''


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def checkout_select():
    """商品選擇頁"""
    # 渲染套餐卡片
    package_cards = ''
    for pid, product in PRODUCTS.items():
        if product['type'] in ['package', 'subscription']:
            package_cards += render_package_card(pid, product)
    
    # 渲染點數卡片
    credits_cards = ''
    for pid, product in PRODUCTS.items():
        if product['type'] == 'credits':
            credits_cards += render_credits_card(pid, product)
    
    html = CHECKOUT_SELECT_HTML.format(
        package_cards=package_cards,
        credits_cards=credits_cards,
        products_json=json.dumps(PRODUCTS, ensure_ascii=False)
    )
    
    return html


@router.post("/confirm", response_class=HTMLResponse)
async def checkout_confirm(product_id: str = Form(...)):
    """確認訂單頁"""
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=400, detail="無效的商品")
    
    product = PRODUCTS[product_id]
    
    type_labels = {
        'package': '單次購買',
        'subscription': '年費訂閱',
        'credits': '點數儲值'
    }
    
    features_html = ''.join([
        f'<li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>{f}</li>'
        for f in product.get('features', [f"{product.get('credits', 0)} 點數"])
    ])
    
    html = CHECKOUT_CONFIRM_HTML.format(
        product_id=product_id,
        icon=product['icon'],
        name=product['name'],
        price=product['price'],
        type_label=type_labels.get(product['type'], ''),
        features_html=features_html
    )
    
    return html


@router.post("/pay")
async def checkout_pay(request: Request, product_id: str = Form(...)):
    """發起支付"""
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=400, detail="無效的商品")
    
    product = PRODUCTS[product_id]
    
    # TODO: 獲取當前用戶 (從 session/JWT)
    user_id = 1  # 暫時硬編碼
    
    try:
        from payment_flow import create_payment
        
        result = create_payment(
            user_id=user_id,
            product_id=product_id,
            product=product
        )
        
        if result.get('success'):
            # 返回綠界支付表單 HTML
            return HTMLResponse(content=result['form_html'])
        else:
            raise HTTPException(status_code=500, detail=result.get('error', '支付建立失敗'))
    
    except ImportError:
        # payment_flow 尚未建立，返回模擬頁面
        return HTMLResponse(content=f'''
        <html>
        <head><title>支付處理中</title></head>
        <body style="text-align:center;padding:50px;">
            <h1>🔄 正在跳轉到綠界支付...</h1>
            <p>商品: {product['name']}</p>
            <p>金額: NT${product['price']}</p>
            <p style="color:red;">（payment_flow 模組尚未載入）</p>
            <a href="/checkout">返回</a>
        </body>
        </html>
        ''')


# 導出商品定義供其他模組使用
def get_product(product_id: str) -> Optional[dict]:
    """獲取商品資訊"""
    return PRODUCTS.get(product_id)

def get_all_products() -> dict:
    """獲取所有商品"""
    return PRODUCTS.copy()

# P4.4: 整合優惠券
CHECKOUT_WITH_COUPON_JS = '''
<script>
async function applyCoupon() {
    const code = document.getElementById('couponCode').value.trim();
    if (!code) return;
    
    const productId = document.getElementById('selectedProduct').value;
    const product = products[productId];
    if (!product) { alert('請先選擇商品'); return; }
    
    const res = await fetch('/api/coupon/verify', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({code: code, amount: product.price, product_id: productId})
    });
    
    const result = await res.json();
    if (result.success && result.valid) {
        document.getElementById('discount').textContent = '- NT$' + result.discount;
        document.getElementById('finalPrice').textContent = 'NT$' + result.final_amount;
        document.getElementById('couponId').value = result.coupon_id;
        alert('優惠券已套用！');
    } else {
        alert(result.detail || '優惠券無效');
    }
}
</script>
'''
