"""
功能權限檢查模組
feature_access.py | @星殼 | 2026-02-18

功能：
- 檢查用戶功能權限
- 追蹤使用次數
- 扣除點數
- 權限摘要
PYLIB: membership_service, db_unified
"""
import sqlite3
from datetime import datetime
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass

# === 配置 ===
DB_PATH = "./beidou_unified.db"

@dataclass
class AccessResult:
    """權限檢查結果"""
    allowed: bool           # 是否允許
    reason: str             # 原因說明
    method: str             # 使用方式: quota/points/locked
    remaining_quota: int    # 剩餘配額 (-1=無限)
    point_cost: int         # 需要點數
    user_points: int        # 用戶點數
    can_use_points: bool    # 可否用點數


# === 功能配置 ===
FEATURE_CONFIG = {
    # feature_code: (name, free, basic, pro, vip, point_cost)
    # -1 = 無限, 0 = 鎖定
    "simple_bazi":   ("簡易八字",    1,  -1, -1, -1, 10),
    "full_bazi":     ("八字報告",    0,   3, -1, -1, 50),
    "ziwei":         ("紫微報告",    0,   3, -1, -1, 50),
    "meihua":        ("梅花易數",    0,   0,  2, -1, 25),
    "qimen":         ("奇門遁甲",    0,   0,  2, -1, 75),
    "zeday":         ("擇日分析",    0,   1,  5, -1, 50),
    "naming":        ("命名建議",    0,   0,  2, -1, 100),
    "match":         ("合婚配對",    0,   0,  1, -1, 75),
    "ai_interpret":  ("AI解讀",      0,   0,  0, -1, 50),
    "full_report":   ("全方位報告",  0,   0,  0,  2, 200),
}

TIER_INDEX = {"free": 1, "basic": 2, "pro": 3, "vip": 4}


def get_db():
    return sqlite3.connect(DB_PATH)


def get_user_info(user_id: int) -> Dict:
    """獲取用戶資訊"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT tier, tier_expires_at, credits 
        FROM auth_users WHERE id = ?
    ''', (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"tier": "free", "expires_at": None, "credits": 0}
    
    tier = row[0] or "free"
    expires_at = row[1]
    credits = row[2] or 0
    
    # 檢查會員是否過期
    if expires_at:
        try:
            exp_dt = datetime.fromisoformat(expires_at)
            if exp_dt < datetime.now():
                tier = "free"
        except:
            pass
    
    return {"tier": tier, "expires_at": expires_at, "credits": credits}


def get_monthly_usage(user_id: int, feature_code: str) -> int:
    """獲取本月使用次數"""
    conn = get_db()
    cursor = conn.cursor()
    
    period = datetime.now().strftime("%Y-%m")
    
    cursor.execute('''
        SELECT usage_count FROM usage_tracking 
        WHERE user_id = ? AND feature_code = ? AND billing_period = ?
    ''', (user_id, feature_code, period))
    
    row = cursor.fetchone()
    conn.close()
    
    return row[0] if row else 0


def check_access(user_id: int, feature_code: str) -> AccessResult:
    """
    檢查用戶是否有權限使用功能
    
    邏輯：
    1. 先檢查會員配額
    2. 配額用完則檢查點數
    3. 都不行則返回鎖定
    """
    # 功能不存在
    if feature_code not in FEATURE_CONFIG:
        return AccessResult(
            allowed=False, reason="功能不存在", method="locked",
            remaining_quota=0, point_cost=0, user_points=0, can_use_points=False
        )
    
    config = FEATURE_CONFIG[feature_code]
    name, free_limit, basic_limit, pro_limit, vip_limit, point_cost = config
    
    # 獲取用戶資訊
    user = get_user_info(user_id)
    tier = user["tier"]
    credits = user["credits"]
    
    # 獲取對應等級的配額
    limits = {
        "free": free_limit,
        "basic": basic_limit,
        "pro": pro_limit,
        "vip": vip_limit
    }
    monthly_limit = limits.get(tier, 0)
    
    # 1. 無限使用
    if monthly_limit == -1:
        return AccessResult(
            allowed=True, reason="會員無限使用", method="quota",
            remaining_quota=-1, point_cost=0, user_points=credits, can_use_points=True
        )
    
    # 2. 有配額限制
    if monthly_limit > 0:
        used = get_monthly_usage(user_id, feature_code)
        remaining = monthly_limit - used
        
        if remaining > 0:
            return AccessResult(
                allowed=True, reason=f"會員配額 (剩餘 {remaining}/{monthly_limit})", 
                method="quota", remaining_quota=remaining, 
                point_cost=0, user_points=credits, can_use_points=True
            )
    
    # 3. 配額用完或無配額，檢查點數
    can_pay = credits >= point_cost
    
    if can_pay:
        return AccessResult(
            allowed=True, reason=f"使用點數 ({point_cost} 點)", 
            method="points", remaining_quota=0, 
            point_cost=point_cost, user_points=credits, can_use_points=True
        )
    
    # 4. 無法使用
    return AccessResult(
        allowed=False, 
        reason=f"需升級會員或購買點數 (需 {point_cost} 點，餘 {credits} 點)",
        method="locked", remaining_quota=0,
        point_cost=point_cost, user_points=credits, can_use_points=False
    )


def consume_access(user_id: int, feature_code: str) -> Tuple[bool, str]:
    """
    消耗權限（使用功能後調用）
    
    Returns: (success, message)
    """
    access = check_access(user_id, feature_code)
    
    if not access.allowed:
        return False, access.reason
    
    conn = get_db()
    cursor = conn.cursor()
    period = datetime.now().strftime("%Y-%m")
    
    try:
        if access.method == "quota":
            # 更新使用次數
            cursor.execute('''
                INSERT INTO usage_tracking 
                    (user_id, feature_code, billing_period, usage_count, last_used_at)
                VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, feature_code, billing_period) 
                DO UPDATE SET 
                    usage_count = usage_count + 1,
                    last_used_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
            ''', (user_id, feature_code, period))
            
            conn.commit()
            conn.close()
            return True, "已使用會員配額"
        
        elif access.method == "points":
            # 扣除點數
            cost = access.point_cost
            
            cursor.execute('''
                UPDATE auth_users 
                SET credits = credits - ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND credits >= ?
            ''', (cost, user_id, cost))
            
            if cursor.rowcount == 0:
                conn.close()
                return False, "點數不足"
            
            # 獲取新餘額
            cursor.execute('SELECT credits FROM auth_users WHERE id = ?', (user_id,))
            new_balance = cursor.fetchone()[0]
            
            # 記錄日誌
            cursor.execute('''
                INSERT INTO credit_logs 
                (user_id, change_type, change_amount, balance_before, balance_after,
                 related_type, description, created_at)
                VALUES (?, 'consume', ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, -cost, new_balance + cost, new_balance, 
                  feature_code, f"使用: {FEATURE_CONFIG[feature_code][0]}"))
            
            conn.commit()
            conn.close()
            return True, f"已扣除 {cost} 點，餘額 {new_balance}"
        
        else:
            conn.close()
            return False, "無法使用"
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)


def get_user_features(user_id: int) -> List[Dict]:
    """
    獲取用戶所有功能權限
    
    Returns: [
        {
            "code": "full_bazi",
            "name": "八字報告",
            "monthly_limit": 3,
            "used": 1,
            "remaining": 2,
            "point_cost": 50,
            "status": "available" | "quota_used" | "locked"
        },
        ...
    ]
    """
    user = get_user_info(user_id)
    tier = user["tier"]
    credits = user["credits"]
    
    features = []
    
    for code, config in FEATURE_CONFIG.items():
        name, free_l, basic_l, pro_l, vip_l, point_cost = config
        
        limits = {"free": free_l, "basic": basic_l, "pro": pro_l, "vip": vip_l}
        monthly_limit = limits.get(tier, 0)
        
        used = get_monthly_usage(user_id, code)
        
        if monthly_limit == -1:
            remaining = -1
            status = "available"
        elif monthly_limit > 0:
            remaining = max(0, monthly_limit - used)
            status = "available" if remaining > 0 else "quota_used"
        else:
            remaining = 0
            status = "locked" if credits < point_cost else "points_only"
        
        features.append({
            "code": code,
            "name": name,
            "monthly_limit": monthly_limit,
            "used": used,
            "remaining": remaining,
            "point_cost": point_cost,
            "status": status
        })
    
    return features


def get_tier_comparison() -> Dict:
    """
    獲取等級比較表（用於定價頁）
    """
    tiers = ["free", "basic", "pro", "vip"]
    tier_names = {
        "free": "免費會員",
        "basic": "基礎會員 $199/月",
        "pro": "專業會員 $499/月",
        "vip": "尊榮會員 $999/月"
    }
    
    comparison = []
    
    for code, config in FEATURE_CONFIG.items():
        name, free_l, basic_l, pro_l, vip_l, point_cost = config
        
        row = {
            "code": code,
            "name": name,
            "point_cost": point_cost,
            "free": _format_limit(free_l),
            "basic": _format_limit(basic_l),
            "pro": _format_limit(pro_l),
            "vip": _format_limit(vip_l),
        }
        comparison.append(row)
    
    return {
        "tier_names": tier_names,
        "features": comparison
    }


def _format_limit(limit: int) -> str:
    """格式化限制顯示"""
    if limit == -1:
        return "無限"
    elif limit == 0:
        return "🔒"
    else:
        return f"{limit}次/月"


# === API 路由整合 ===
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/access", tags=["功能權限"])

class AccessCheckResponse(BaseModel):
    allowed: bool
    reason: str
    method: str
    remaining_quota: int
    point_cost: int
    user_points: int
    can_use_points: bool

@router.get("/check/{feature_code}", response_model=AccessCheckResponse)
async def api_check_access(feature_code: str, request: Request):
    """檢查功能權限"""
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(status_code=401, detail="請先登入")
    
    result = check_access(user_id, feature_code)
    return AccessCheckResponse(
        allowed=result.allowed,
        reason=result.reason,
        method=result.method,
        remaining_quota=result.remaining_quota,
        point_cost=result.point_cost,
        user_points=result.user_points,
        can_use_points=result.can_use_points
    )

@router.get("/features")
async def api_get_features(request: Request):
    """獲取用戶所有功能權限"""
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(status_code=401, detail="請先登入")
    
    return {
        "user": get_user_info(user_id),
        "features": get_user_features(user_id)
    }

@router.get("/tiers")
async def api_get_tiers():
    """獲取等級比較表"""
    return get_tier_comparison()


# === 測試 ===
if __name__ == "__main__":
    print("【功能權限測試】\n")
    
    # 顯示等級比較表
    comp = get_tier_comparison()
    print("功能權限矩陣：")
    print(f"{'功能':<12} {'免費':<8} {'基礎':<8} {'專業':<8} {'尊榮':<8} {'點數'}")
    print("-" * 60)
    for f in comp["features"]:
        print(f"{f['name']:<10} {f['free']:<8} {f['basic']:<8} {f['pro']:<8} {f['vip']:<8} {f['point_cost']}")


print("✓ 功能權限模組已載入")
