"""
管理統計 API
admin_stats_api.py | @理樞 | 2026-02-17
PYLIB: db_unified, auth_jwt
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from datetime import datetime, timedelta
import sqlite3
from typing import Optional

router = APIRouter(prefix="/api/admin", tags=["admin-stats"])

DB_PATH = 'beidou_unified.db'

def require_admin(request: Request):
    """驗證管理員權限 (TODO: 整合 JWT)"""
    # 暫時跳過驗證
    return True

@router.get("/stats/users")
async def get_user_stats(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    _: bool = Depends(require_admin)
):
    """
    A3.7: GET /api/admin/stats/users
    用戶統計
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        # 總用戶數
        cursor.execute('SELECT COUNT(*) FROM users')
        stats['total_users'] = cursor.fetchone()[0]
        
        # 新用戶 (指定天數內)
        since = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM users WHERE created_at >= ?', (since,))
        stats['new_users'] = cursor.fetchone()[0]
        
        # 活躍用戶 (有登入記錄)
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE last_login >= ?
        ''', (since,))
        result = cursor.fetchone()
        stats['active_users'] = result[0] if result else 0
        
        # 會員分佈
        try:
            cursor.execute('''
                SELECT tier, COUNT(*) FROM memberships 
                WHERE status = 'active'
                GROUP BY tier
            ''')
            stats['membership_distribution'] = {row[0]: row[1] for row in cursor.fetchall()}
        except:
            stats['membership_distribution'] = {}
        
        # 每日新增用戶趨勢 (最近 7 天)
        daily_trend = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(*) FROM users 
                WHERE DATE(created_at) = ?
            ''', (date,))
            daily_trend.append({'date': date, 'count': cursor.fetchone()[0]})
        
        stats['daily_trend'] = list(reversed(daily_trend))
        stats['period_days'] = days
        
        return {"success": True, "stats": stats}
        
    finally:
        conn.close()


@router.get("/stats/orders")
async def get_order_stats(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    _: bool = Depends(require_admin)
):
    """
    A3.8: GET /api/admin/stats/orders
    訂單統計
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        stats = {}
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        # 總訂單數
        try:
            cursor.execute('SELECT COUNT(*) FROM orders')
            stats['total_orders'] = cursor.fetchone()[0]
        except:
            stats['total_orders'] = 0
        
        # 期間內訂單
        try:
            cursor.execute('SELECT COUNT(*) FROM orders WHERE created_at >= ?', (since,))
            stats['period_orders'] = cursor.fetchone()[0]
        except:
            stats['period_orders'] = 0
        
        # 已支付訂單
        try:
            cursor.execute('''
                SELECT COUNT(*) FROM orders 
                WHERE status = 'paid' AND created_at >= ?
            ''', (since,))
            stats['paid_orders'] = cursor.fetchone()[0]
        except:
            stats['paid_orders'] = 0
        
        # 訂單狀態分佈
        try:
            cursor.execute('''
                SELECT status, COUNT(*) FROM orders 
                WHERE created_at >= ?
                GROUP BY status
            ''', (since,))
            stats['status_distribution'] = {row[0]: row[1] for row in cursor.fetchall()}
        except:
            stats['status_distribution'] = {}
        
        # 產品銷售排行
        try:
            cursor.execute('''
                SELECT product_name, COUNT(*), SUM(amount) FROM orders 
                WHERE status = 'paid' AND created_at >= ?
                GROUP BY product_name
                ORDER BY COUNT(*) DESC
                LIMIT 10
            ''', (since,))
            stats['top_products'] = [
                {'name': row[0], 'count': row[1], 'revenue': row[2]}
                for row in cursor.fetchall()
            ]
        except:
            stats['top_products'] = []
        
        stats['period_days'] = days
        
        return {"success": True, "stats": stats}
        
    finally:
        conn.close()


@router.get("/stats/revenue")
async def get_revenue_stats(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    _: bool = Depends(require_admin)
):
    """
    A3.9: GET /api/admin/stats/revenue
    營收統計
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        stats = {}
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        # 總營收
        try:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM orders 
                WHERE status = 'paid'
            ''')
            stats['total_revenue'] = cursor.fetchone()[0]
        except:
            stats['total_revenue'] = 0
        
        # 期間營收
        try:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM orders 
                WHERE status = 'paid' AND paid_at >= ?
            ''', (since,))
            stats['period_revenue'] = cursor.fetchone()[0]
        except:
            stats['period_revenue'] = 0
        
        # 每日營收趨勢
        daily_revenue = []
        for i in range(min(days, 30)):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            try:
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) FROM orders 
                    WHERE status = 'paid' AND DATE(paid_at) = ?
                ''', (date,))
                daily_revenue.append({'date': date, 'revenue': cursor.fetchone()[0]})
            except:
                daily_revenue.append({'date': date, 'revenue': 0})
        
        stats['daily_trend'] = list(reversed(daily_revenue))
        
        # 平均客單價
        try:
            cursor.execute('''
                SELECT AVG(amount) FROM orders 
                WHERE status = 'paid' AND paid_at >= ?
            ''', (since,))
            avg = cursor.fetchone()[0]
            stats['avg_order_value'] = round(avg, 2) if avg else 0
        except:
            stats['avg_order_value'] = 0
        
        # 營收來源分佈
        try:
            cursor.execute('''
                SELECT order_type, SUM(amount) FROM orders 
                WHERE status = 'paid' AND paid_at >= ?
                GROUP BY order_type
            ''', (since,))
            stats['revenue_by_type'] = {row[0]: row[1] for row in cursor.fetchall()}
        except:
            stats['revenue_by_type'] = {}
        
        stats['period_days'] = days
        
        return {"success": True, "stats": stats}
        
    finally:
        conn.close()


@router.get("/stats/summary")
async def get_summary_stats(
    request: Request,
    _: bool = Depends(require_admin)
):
    """
    綜合儀表板統計
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        summary = {}
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 今日新用戶
        try:
            cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?', (today,))
            summary['today_users'] = cursor.fetchone()[0]
        except:
            summary['today_users'] = 0
        
        # 今日訂單
        try:
            cursor.execute('SELECT COUNT(*) FROM orders WHERE DATE(created_at) = ?', (today,))
            summary['today_orders'] = cursor.fetchone()[0]
        except:
            summary['today_orders'] = 0
        
        # 今日營收
        try:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM orders 
                WHERE status = 'paid' AND DATE(paid_at) = ?
            ''', (today,))
            summary['today_revenue'] = cursor.fetchone()[0]
        except:
            summary['today_revenue'] = 0
        
        # 待處理訂單
        try:
            cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
            summary['pending_orders'] = cursor.fetchone()[0]
        except:
            summary['pending_orders'] = 0
        
        return {"success": True, "summary": summary}
        
    finally:
        conn.close()
