"""
會員訂閱服務模組
M8.1-M8.7 | @星殼 | 2026-02-17
PYLIB: db_unified, payment_service, email_service
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
import sqlite3

class MembershipTier(Enum):
    """會員等級"""
    FREE = "free"
    BASIC = "basic"         # 基礎命盤 NT$299
    PREMIUM = "premium"     # 尊榮會員 NT$1,999/年
    FAMILY = "family"       # 家族方案 NT$4,999/年

@dataclass
class MembershipPlan:
    """會員方案"""
    tier: MembershipTier
    name: str
    price: int
    duration_days: int
    features: list
    max_members: int = 1

# 方案定義
MEMBERSHIP_PLANS = {
    'basic': MembershipPlan(
        tier=MembershipTier.BASIC,
        name='基礎命盤',
        price=299,
        duration_days=0,  # 單次
        features=['八字四柱', '五行分析', '十神分析', 'PDF報告'],
        max_members=1
    ),
    'premium': MembershipPlan(
        tier=MembershipTier.PREMIUM,
        name='尊榮會員',
        price=1999,
        duration_days=365,
        features=['完整命理', '每月運勢', '3次擇日', '1次命名', '無限合婚', '專屬客服'],
        max_members=1
    ),
    'family': MembershipPlan(
        tier=MembershipTier.FAMILY,
        name='家族方案',
        price=4999,
        duration_days=365,
        features=['尊榮會員×5', '家族分析', '12次擇日', '5次命名', '優先客服'],
        max_members=5
    ),
}

class MembershipService:
    """會員服務"""
    
    def __init__(self, db_path: str = "beidou_unified.db"):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """初始化會員表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memberships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tier TEXT NOT NULL DEFAULT 'free',
                start_date TEXT,
                end_date TEXT,
                auto_renew INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS membership_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                tier TEXT,
                amount INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_membership(self, user_id: int) -> Dict[str, Any]:
        """獲取用戶會員狀態"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tier, start_date, end_date, auto_renew 
            FROM memberships WHERE user_id = ? 
            ORDER BY id DESC LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {
                'tier': MembershipTier.FREE.value,
                'name': '免費用戶',
                'is_active': True,
                'end_date': None,
                'auto_renew': False,
                'days_left': None
            }
        
        tier, start_date, end_date, auto_renew = row
        
        # 檢查是否過期
        is_active = True
        days_left = None
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            is_active = end_dt > datetime.now()
            days_left = (end_dt - datetime.now()).days if is_active else 0
        
        plan = MEMBERSHIP_PLANS.get(tier)
        name = plan.name if plan else '免費用戶'
        
        return {
            'tier': tier,
            'name': name,
            'is_active': is_active,
            'start_date': start_date,
            'end_date': end_date,
            'auto_renew': bool(auto_renew),
            'days_left': days_left
        }
    
    def subscribe(self, user_id: int, plan_code: str, payment_id: str = None) -> Dict[str, Any]:
        """訂閱會員"""
        plan = MEMBERSHIP_PLANS.get(plan_code)
        if not plan:
            return {'success': False, 'error': '無效的方案'}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        end_date = None
        if plan.duration_days > 0:
            end_date = (now + timedelta(days=plan.duration_days)).isoformat()
        
        # 插入會員記錄
        cursor.execute('''
            INSERT INTO memberships (user_id, tier, start_date, end_date, auto_renew)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, plan.tier.value, now.isoformat(), end_date, 0))
        
        # 記錄歷史
        cursor.execute('''
            INSERT INTO membership_history (user_id, action, tier, amount)
            VALUES (?, 'subscribe', ?, ?)
        ''', (user_id, plan.tier.value, plan.price))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'tier': plan.tier.value,
            'name': plan.name,
            'end_date': end_date
        }
    
    def cancel_subscription(self, user_id: int) -> Dict[str, Any]:
        """取消訂閱 (不立即生效，到期後不續訂)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE memberships SET auto_renew = 0, updated_at = ?
            WHERE user_id = ? AND end_date > ?
        ''', (datetime.now().isoformat(), user_id, datetime.now().isoformat()))
        
        cursor.execute('''
            INSERT INTO membership_history (user_id, action, tier)
            VALUES (?, 'cancel', NULL)
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': '已取消自動續訂，當前會員資格將持續至到期日'}
    
    def check_permission(self, user_id: int, feature: str) -> bool:
        """檢查用戶是否有權限使用某功能"""
        membership = self.get_membership(user_id)
        
        if not membership['is_active']:
            return False
        
        tier = membership['tier']
        
        # 權限映射
        permissions = {
            'free': ['bazi_basic', 'wuxing'],
            'basic': ['bazi_basic', 'wuxing', 'shishen', 'pdf_basic'],
            'premium': ['bazi_basic', 'wuxing', 'shishen', 'ziwei', 'dayun', 'liunian', 
                       'zeri', 'naming', 'matching', 'pdf_full', 'monthly_update'],
            'family': ['bazi_basic', 'wuxing', 'shishen', 'ziwei', 'dayun', 'liunian',
                      'zeri', 'naming', 'matching', 'pdf_full', 'monthly_update', 'family_analysis'],
        }
        
        allowed = permissions.get(tier, permissions['free'])
        return feature in allowed
    
    def get_expiring_members(self, days: int = 7) -> list:
        """獲取即將到期的會員 (用於發送提醒)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        future = (datetime.now() + timedelta(days=days)).isoformat()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            SELECT m.user_id, m.tier, m.end_date, u.email, u.username
            FROM memberships m
            JOIN users u ON m.user_id = u.id
            WHERE m.end_date > ? AND m.end_date <= ?
            AND m.auto_renew = 0
        ''', (now, future))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {'user_id': r[0], 'tier': r[1], 'end_date': r[2], 'email': r[3], 'username': r[4]}
            for r in results
        ]

# 單例
membership_service = MembershipService()

if __name__ == "__main__":
    ms = MembershipService()
    print("✓ 會員服務模組已載入")
    print(f"方案數量: {len(MEMBERSHIP_PLANS)}")
    for code, plan in MEMBERSHIP_PLANS.items():
        print(f"  - {code}: {plan.name} NT${plan.price}")
