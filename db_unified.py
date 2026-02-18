#!/usr/bin/env python3
"""
db_unified.py - 北斗命數統一數據庫
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
統一管理所有數據：
  • 用戶認證 (auth_users)
  • 用戶資料 (user_profiles)
  • 命理分析 (bazi_records, ziwei_records, meihua_records)
  • 擇日記錄 (date_records)
  • 報告記錄 (report_records)
  • 購買/點數 (purchase_records, credit_logs)
  • 操作日誌 (activity_logs)
═══════════════════════════════════════════════════════════════════════

XTF Task Chain
@11星協作：@織明(統籌) @流祇(連結) @星殼(架構)
"""

import sqlite3
import hashlib
import secrets
import uuid
import json
import os
from typing import Dict, Optional, List, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from contextlib import contextmanager
from enum import Enum

# ════════════════════════════════════════════════════════════════════
# L0: 配置
# ════════════════════════════════════════════════════════════════════

DB_PATH = os.environ.get("BEIDOU_DB_PATH", "./beidou_unified.db")

class RecordType(Enum):
    BAZI = "bazi"
    ZIWEI = "ziwei"
    MEIHUA = "meihua"
    DATE_MARRY = "date_marry"
    DATE_GROUND = "date_ground"
    DATE_EVENT = "date_event"
    MATCH = "match"
    REPORT = "report"

# ════════════════════════════════════════════════════════════════════
# L1: 統一 Schema
# ════════════════════════════════════════════════════════════════════

UNIFIED_SCHEMA = """
-- ════════════════════════════════════════════════════════════════════
-- 北斗命數統一數據庫 Schema v1.0
-- 建立日期：2026-02-17
-- ════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- 1. 用戶認證
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS auth_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    display_name TEXT,
    phone TEXT,
    avatar_url TEXT,
    
    -- 點數與訂閱
    credits INTEGER DEFAULT 100,
    tier TEXT DEFAULT 'free',
    tier_expires_at TEXT,
    
    -- 狀態
    is_active INTEGER DEFAULT 1,
    is_verified INTEGER DEFAULT 0,
    is_admin INTEGER DEFAULT 0,
    
    -- 登入資訊
    last_login_at TEXT,
    last_login_ip TEXT,
    login_count INTEGER DEFAULT 0,
    
    -- 時間戳
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT DEFAULT (datetime('now', 'localtime'))
);

-- ─────────────────────────────────────────────────────────────────────
-- 2. 用戶出生資料（可多筆，支援家人）
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    profile_type TEXT DEFAULT 'self',  -- self/family/friend/client
    name TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('男', '女')),
    
    -- 出生資料
    birth_year INTEGER,
    birth_month INTEGER,
    birth_day INTEGER,
    birth_hour INTEGER,
    birth_minute INTEGER DEFAULT 0,
    is_lunar INTEGER DEFAULT 0,
    is_leap_month INTEGER DEFAULT 0,
    birth_place TEXT,
    timezone TEXT DEFAULT 'Asia/Taipei',
    
    -- 計算後的干支
    year_gz TEXT,
    month_gz TEXT,
    day_gz TEXT,
    hour_gz TEXT,
    
    -- 標記
    is_primary INTEGER DEFAULT 0,
    notes TEXT,
    
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────────
-- 3. 八字分析記錄
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bazi_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    profile_id INTEGER,
    
    -- 四柱
    year_gz TEXT NOT NULL,
    month_gz TEXT NOT NULL,
    day_gz TEXT NOT NULL,
    hour_gz TEXT NOT NULL,
    
    -- 分析結果
    day_master TEXT,
    day_master_wx TEXT,
    strength_level TEXT,
    yongshen TEXT,
    xishen TEXT,
    jishen TEXT,
    
    -- 五行統計
    wx_count TEXT,  -- JSON: {"木":2, "火":1, ...}
    
    -- 格局
    geju_name TEXT,
    geju_field TEXT,
    
    -- 大運（JSON）
    dayun_data TEXT,
    
    -- 版本
    calc_version TEXT DEFAULT '1.0',
    
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES user_profiles(id) ON DELETE SET NULL
);

-- ─────────────────────────────────────────────────────────────────────
-- 4. 紫微斗數記錄
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ziwei_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    profile_id INTEGER,
    
    -- 基本
    ju_shu INTEGER,
    ming_gong TEXT,
    ming_gong_idx INTEGER,
    shen_gong TEXT,
    shen_gong_idx INTEGER,
    
    -- 星曜（JSON）
    ming_stars TEXT,
    shen_stars TEXT,
    
    -- 四化
    sihua_lu TEXT,
    sihua_quan TEXT,
    sihua_ke TEXT,
    sihua_ji TEXT,
    
    -- 十二宮（JSON）
    gongs_data TEXT,
    
    -- 版本
    calc_version TEXT DEFAULT '1.0',
    
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES user_profiles(id) ON DELETE SET NULL
);

-- ─────────────────────────────────────────────────────────────────────
-- 5. 梅花易數記錄
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS meihua_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- 起卦資訊
    question TEXT,
    divine_method TEXT DEFAULT 'time',  -- time/number/word
    divine_params TEXT,  -- JSON
    
    -- 卦象
    ben_gua TEXT,
    bian_gua TEXT,
    hu_gua TEXT,
    dong_yao INTEGER,
    
    -- 體用
    ti_gua TEXT,
    yong_gua TEXT,
    ti_yong_relation TEXT,
    
    -- 斷卦
    verdict TEXT,
    analysis TEXT,
    
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────────
-- 6. 擇日記錄
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS date_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- 類型
    date_type TEXT NOT NULL,  -- marry/ground/kaishi/banjia/...
    
    -- 查詢條件
    query_params TEXT,  -- JSON
    
    -- 結果（JSON）
    selected_dates TEXT,
    top_date TEXT,
    top_score REAL,
    
    -- 最終選擇
    final_date TEXT,
    final_rike TEXT,
    
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────────
-- 7. 合婚/配對記錄
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS match_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- 類型
    match_type TEXT DEFAULT 'marriage',  -- marriage/parent/partner
    
    -- 雙方資料
    person1_data TEXT,  -- JSON
    person2_data TEXT,  -- JSON
    
    -- 結果
    score INTEGER,
    grade TEXT,
    percentage INTEGER,
    factors TEXT,  -- JSON
    summary TEXT,
    advice TEXT,
    
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────────
-- 8. 報告記錄
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS report_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- 報告資訊
    report_type TEXT NOT NULL,  -- bazi/ziwei/marry/...
    report_level TEXT,  -- L1/L2/L3/L4
    report_format TEXT DEFAULT 'pdf',  -- pdf/html/md
    
    -- 關聯
    source_record_id INTEGER,
    source_record_type TEXT,
    
    -- 內容
    report_title TEXT,
    report_data TEXT,  -- JSON or content
    file_path TEXT,
    
    -- 點數
    credits_used INTEGER DEFAULT 0,
    
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────────
-- 9. 購買記錄
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS purchase_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- 訂單
    order_no TEXT UNIQUE NOT NULL,
    plan_code TEXT NOT NULL,
    plan_name TEXT,
    amount INTEGER NOT NULL,
    currency TEXT DEFAULT 'TWD',
    
    -- 支付
    payment_provider TEXT,  -- ecpay/newebpay
    payment_method TEXT,
    trade_no TEXT,
    
    -- 狀態
    status TEXT DEFAULT 'pending',  -- pending/paid/failed/refunded
    paid_at TEXT,
    
    -- 點數
    credits_added INTEGER DEFAULT 0,
    
    -- 通知
    notify_data TEXT,  -- JSON
    
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────────
-- 10. 點數流水
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS credit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- 變動
    change_type TEXT NOT NULL,  -- purchase/use/refund/bonus/admin
    change_amount INTEGER NOT NULL,
    balance_before INTEGER,
    balance_after INTEGER,
    
    -- 關聯
    related_id INTEGER,
    related_type TEXT,
    
    -- 說明
    description TEXT,
    
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────────
-- 11. 操作日誌
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    
    -- 操作
    action TEXT NOT NULL,  -- login/logout/register/query/report/...
    action_detail TEXT,
    
    -- 請求
    ip_address TEXT,
    user_agent TEXT,
    request_path TEXT,
    
    -- 結果
    is_success INTEGER DEFAULT 1,
    error_message TEXT,
    
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

-- ─────────────────────────────────────────────────────────────────────
-- 12. 回饋記錄
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS feedback_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    
    -- 回饋
    feedback_type TEXT DEFAULT 'general',
    rating INTEGER,
    q1_answer TEXT,
    q2_answer TEXT,
    q3_answer TEXT,
    suggestion TEXT,
    
    -- 關聯
    related_report_id INTEGER,
    
    -- 處理
    is_processed INTEGER DEFAULT 0,
    admin_notes TEXT,
    
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

-- ─────────────────────────────────────────────────────────────────────
-- 索引
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_auth_users_username ON auth_users(username);
CREATE INDEX IF NOT EXISTS idx_auth_users_email ON auth_users(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_user ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_bazi_user ON bazi_records(user_id);
CREATE INDEX IF NOT EXISTS idx_ziwei_user ON ziwei_records(user_id);
CREATE INDEX IF NOT EXISTS idx_meihua_user ON meihua_records(user_id);
CREATE INDEX IF NOT EXISTS idx_date_user ON date_records(user_id);
CREATE INDEX IF NOT EXISTS idx_match_user ON match_records(user_id);
CREATE INDEX IF NOT EXISTS idx_report_user ON report_records(user_id);
CREATE INDEX IF NOT EXISTS idx_purchase_user ON purchase_records(user_id);
CREATE INDEX IF NOT EXISTS idx_purchase_order ON purchase_records(order_no);
CREATE INDEX IF NOT EXISTS idx_credit_user ON credit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_action ON activity_logs(action);
"""

# ════════════════════════════════════════════════════════════════════
# L2: 數據庫管理器
# ════════════════════════════════════════════════════════════════════

class UnifiedDB:
    """統一數據庫管理器"""
    
    _instance = None
    
    def __new__(cls, db_path: str = DB_PATH):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = DB_PATH):
        if self._initialized:
            return
        self.db_path = db_path
        self._init_db()
        self._initialized = True
    
    def _init_db(self):
        """初始化數據庫"""
        with self._get_conn() as conn:
            conn.executescript(UNIFIED_SCHEMA)
            conn.commit()
        print(f"✅ 數據庫初始化：{self.db_path}")
    
    @contextmanager
    def _get_conn(self):
        """獲取連接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()
    
    # ─────────────────────────────────────────────────────────────
    # 通用 CRUD
    # ─────────────────────────────────────────────────────────────
    
    def insert(self, table: str, data: dict) -> int:
        """插入記錄"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        with self._get_conn() as conn:
            cursor = conn.execute(sql, list(data.values()))
            conn.commit()
            return cursor.lastrowid
    
    def update(self, table: str, record_id: int, data: dict) -> bool:
        """更新記錄"""
        # 檢查表是否有 updated_at 欄位
        with self._get_conn() as conn:
            cursor = conn.execute(f"PRAGMA table_info({table})")
            columns = [row['name'] for row in cursor.fetchall()]
            
            if 'updated_at' in columns and 'updated_at' not in data:
                data['updated_at'] = datetime.now().isoformat()
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        
        with self._get_conn() as conn:
            conn.execute(sql, list(data.values()) + [record_id])
            conn.commit()
        return True
    
    def delete(self, table: str, record_id: int) -> bool:
        """刪除記錄"""
        with self._get_conn() as conn:
            conn.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
            conn.commit()
        return True
    
    def get_by_id(self, table: str, record_id: int) -> Optional[dict]:
        """根據 ID 獲取"""
        with self._get_conn() as conn:
            row = conn.execute(
                f"SELECT * FROM {table} WHERE id = ?", (record_id,)
            ).fetchone()
            return dict(row) if row else None
    
    def query(self, table: str, where: dict = None, 
              order_by: str = None, limit: int = None) -> List[dict]:
        """查詢記錄"""
        sql = f"SELECT * FROM {table}"
        params = []
        
        if where:
            conditions = ' AND '.join([f"{k} = ?" for k in where.keys()])
            sql += f" WHERE {conditions}"
            params = list(where.values())
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        with self._get_conn() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(row) for row in rows]
    
    # ─────────────────────────────────────────────────────────────
    # 用戶管理
    # ─────────────────────────────────────────────────────────────
    
    def create_user(self, username: str, password: str, 
                    email: str = "", display_name: str = "") -> Tuple[bool, str, Optional[int]]:
        """創建用戶"""
        # 檢查用戶名
        existing = self.query("auth_users", {"username": username}, limit=1)
        if existing:
            return False, "用戶名已存在", None
        
        # 密碼雜湊
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        
        user_id = self.insert("auth_users", {
            "uuid": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "salt": salt,
            "display_name": display_name or username,
        })
        
        self.log_activity(user_id, "register", f"用戶註冊：{username}")
        return True, "註冊成功", user_id
    
    def verify_login(self, username: str, password: str) -> Tuple[bool, Optional[dict]]:
        """驗證登入"""
        users = self.query("auth_users", {"username": username}, limit=1)
        if not users:
            return False, None
        
        user = users[0]
        if not user['is_active']:
            return False, None
        
        password_hash = hashlib.sha256(f"{password}{user['salt']}".encode()).hexdigest()
        if password_hash != user['password_hash']:
            self.log_activity(None, "login_failed", f"登入失敗：{username}")
            return False, None
        
        # 更新登入資訊
        self.update("auth_users", user['id'], {
            "last_login_at": datetime.now().isoformat(),
            "login_count": user['login_count'] + 1,
        })
        
        self.log_activity(user['id'], "login", f"用戶登入：{username}")
        return True, user
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """獲取用戶"""
        return self.get_by_id("auth_users", user_id)
    
    def update_credits(self, user_id: int, amount: int, 
                       change_type: str, description: str = "") -> Tuple[bool, int]:
        """更新點數"""
        user = self.get_user(user_id)
        if not user:
            return False, 0
        
        new_credits = user['credits'] + amount
        if new_credits < 0:
            return False, user['credits']
        
        # 更新用戶
        self.update("auth_users", user_id, {"credits": new_credits})
        
        # 記錄流水
        self.insert("credit_logs", {
            "user_id": user_id,
            "change_type": change_type,
            "change_amount": amount,
            "balance_before": user['credits'],
            "balance_after": new_credits,
            "description": description,
        })
        
        return True, new_credits
    
    # ─────────────────────────────────────────────────────────────
    # 用戶資料
    # ─────────────────────────────────────────────────────────────
    
    def add_profile(self, user_id: int, data: dict) -> int:
        """添加用戶資料"""
        data['user_id'] = user_id
        return self.insert("user_profiles", data)
    
    def get_profiles(self, user_id: int) -> List[dict]:
        """獲取用戶所有資料"""
        return self.query("user_profiles", {"user_id": user_id}, order_by="is_primary DESC, created_at")
    
    def get_primary_profile(self, user_id: int) -> Optional[dict]:
        """獲取主要資料"""
        profiles = self.query("user_profiles", {"user_id": user_id, "is_primary": 1}, limit=1)
        return profiles[0] if profiles else None
    
    # ─────────────────────────────────────────────────────────────
    # 命理記錄
    # ─────────────────────────────────────────────────────────────
    
    def save_bazi(self, user_id: int, data: dict) -> int:
        """保存八字分析"""
        data['user_id'] = user_id
        record_id = self.insert("bazi_records", data)
        self.log_activity(user_id, "bazi_analysis", f"八字分析 #{record_id}")
        return record_id
    
    def save_ziwei(self, user_id: int, data: dict) -> int:
        """保存紫微分析"""
        data['user_id'] = user_id
        record_id = self.insert("ziwei_records", data)
        self.log_activity(user_id, "ziwei_analysis", f"紫微分析 #{record_id}")
        return record_id
    
    def save_meihua(self, user_id: int, data: dict) -> int:
        """保存梅花分析"""
        data['user_id'] = user_id
        record_id = self.insert("meihua_records", data)
        self.log_activity(user_id, "meihua_divine", f"梅花起卦 #{record_id}")
        return record_id
    
    def save_date_selection(self, user_id: int, data: dict) -> int:
        """保存擇日記錄"""
        data['user_id'] = user_id
        record_id = self.insert("date_records", data)
        self.log_activity(user_id, "date_selection", f"擇日 #{record_id}")
        return record_id
    
    def save_match(self, user_id: int, data: dict) -> int:
        """保存合婚記錄"""
        data['user_id'] = user_id
        record_id = self.insert("match_records", data)
        self.log_activity(user_id, "match_analysis", f"合婚分析 #{record_id}")
        return record_id
    
    # ─────────────────────────────────────────────────────────────
    # 報告
    # ─────────────────────────────────────────────────────────────
    
    def save_report(self, user_id: int, data: dict, credits_used: int = 0) -> int:
        """保存報告"""
        data['user_id'] = user_id
        data['credits_used'] = credits_used
        
        if credits_used > 0:
            success, _ = self.update_credits(user_id, -credits_used, "use", f"報告：{data.get('report_type')}")
            if not success:
                raise ValueError("點數不足")
        
        record_id = self.insert("report_records", data)
        self.log_activity(user_id, "report_generate", f"報告 #{record_id}")
        return record_id
    
    def get_user_reports(self, user_id: int, limit: int = 20) -> List[dict]:
        """獲取用戶報告"""
        return self.query("report_records", {"user_id": user_id}, 
                         order_by="created_at DESC", limit=limit)
    
    # ─────────────────────────────────────────────────────────────
    # 購買
    # ─────────────────────────────────────────────────────────────
    
    def create_order(self, user_id: int, order_no: str, 
                     plan_code: str, plan_name: str, amount: int) -> int:
        """創建訂單"""
        return self.insert("purchase_records", {
            "user_id": user_id,
            "order_no": order_no,
            "plan_code": plan_code,
            "plan_name": plan_name,
            "amount": amount,
            "status": "pending",
        })
    
    def complete_order(self, order_no: str, trade_no: str, 
                       credits_to_add: int, notify_data: str = "") -> bool:
        """完成訂單"""
        orders = self.query("purchase_records", {"order_no": order_no}, limit=1)
        if not orders:
            return False
        
        order = orders[0]
        
        # 更新訂單
        self.update("purchase_records", order['id'], {
            "status": "paid",
            "trade_no": trade_no,
            "paid_at": datetime.now().isoformat(),
            "credits_added": credits_to_add,
            "notify_data": notify_data,
        })
        
        # 增加點數
        self.update_credits(order['user_id'], credits_to_add, "purchase", f"訂單：{order_no}")
        
        self.log_activity(order['user_id'], "purchase_complete", f"訂單完成：{order_no}")
        return True
    
    # ─────────────────────────────────────────────────────────────
    # 日誌
    # ─────────────────────────────────────────────────────────────
    
    def log_activity(self, user_id: Optional[int], action: str, 
                     detail: str = "", ip: str = "", ua: str = ""):
        """記錄操作"""
        self.insert("activity_logs", {
            "user_id": user_id,
            "action": action,
            "action_detail": detail,
            "ip_address": ip,
            "user_agent": ua,
        })
    
    # ─────────────────────────────────────────────────────────────
    # 統計
    # ─────────────────────────────────────────────────────────────
    
    def get_stats(self) -> dict:
        """獲取統計"""
        with self._get_conn() as conn:
            stats = {}
            tables = [
                ("users", "auth_users"),
                ("profiles", "user_profiles"),
                ("bazi", "bazi_records"),
                ("ziwei", "ziwei_records"),
                ("meihua", "meihua_records"),
                ("dates", "date_records"),
                ("matches", "match_records"),
                ("reports", "report_records"),
                ("purchases", "purchase_records"),
            ]
            
            for name, table in tables:
                row = conn.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
                stats[name] = row['cnt']
            
            # 活躍用戶
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM auth_users WHERE last_login_at > ?",
                (week_ago,)
            ).fetchone()
            stats['active_users_7d'] = row['cnt']
            
            # 總收入
            row = conn.execute(
                "SELECT SUM(amount) as total FROM purchase_records WHERE status = 'paid'"
            ).fetchone()
            stats['total_revenue'] = row['total'] or 0
            
            return stats


# ════════════════════════════════════════════════════════════════════
# L3: FastAPI 整合
# ════════════════════════════════════════════════════════════════════

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import base64
import hmac

app = FastAPI(title="北斗命數統一 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局實例
db = UnifiedDB()
security = HTTPBearer(auto_error=False)

# JWT 配置
JWT_SECRET = os.environ.get("JWT_SECRET", "beidou_secret_2026")
TOKEN_EXPIRE = 24 * 60  # 24小時

# ─────────────────────────────────────────────────────────────
# JWT 工具
# ─────────────────────────────────────────────────────────────

def create_token(user_id: int, username: str) -> str:
    """創建 Token"""
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).rstrip(b'=').decode()
    payload_data = {
        "user_id": user_id,
        "username": username,
        "exp": int(time.time()) + TOKEN_EXPIRE * 60,
        "iat": int(time.time()),
    }
    payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).rstrip(b'=').decode()
    signature = base64.urlsafe_b64encode(
        hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    ).rstrip(b'=').decode()
    return f"{header}.{payload}.{signature}"

def verify_token(token: str) -> Optional[dict]:
    """驗證 Token"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header, payload, signature = parts
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        ).rstrip(b'=').decode()
        
        if signature != expected_sig:
            return None
        
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        payload_data = json.loads(base64.urlsafe_b64decode(payload))
        
        if payload_data.get('exp', 0) < time.time():
            return None
        
        return payload_data
    except:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """獲取當前用戶"""
    if not credentials:
        return None
    payload = verify_token(credentials.credentials)
    return payload

async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """要求認證"""
    if not credentials:
        raise HTTPException(401, "需要認證")
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(401, "Token 無效或已過期")
    return payload

# ─────────────────────────────────────────────────────────────
# 請求模型
# ─────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class ProfileRequest(BaseModel):
    name: str
    gender: str
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int = 12
    is_lunar: bool = False
    birth_place: Optional[str] = None
    profile_type: str = "self"

class SaveRecordRequest(BaseModel):
    record_type: str
    data: dict

# ─────────────────────────────────────────────────────────────
# API 端點
# ─────────────────────────────────────────────────────────────

@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    """註冊"""
    success, msg, user_id = db.create_user(req.username, req.password, req.email or "")
    if not success:
        raise HTTPException(400, msg)
    
    user = db.get_user(user_id)
    return {
        "success": True,
        "message": msg,
        "user": {"id": user_id, "username": req.username, "credits": user['credits']}
    }

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    """登入"""
    success, user = db.verify_login(req.username, req.password)
    if not success:
        raise HTTPException(401, "用戶名或密碼錯誤")
    
    token = create_token(user['id'], user['username'])
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": TOKEN_EXPIRE * 60,
        "user": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "credits": user['credits'],
            "tier": user['tier'],
        }
    }

@app.get("/api/auth/me")
async def get_me(user: dict = Depends(require_auth)):
    """當前用戶"""
    user_data = db.get_user(user['user_id'])
    if not user_data:
        raise HTTPException(404, "用戶不存在")
    return user_data

@app.post("/api/profile")
async def add_profile(req: ProfileRequest, user: dict = Depends(require_auth)):
    """添加資料"""
    profile_id = db.add_profile(user['user_id'], req.dict())
    return {"success": True, "profile_id": profile_id}

@app.get("/api/profiles")
async def get_profiles(user: dict = Depends(require_auth)):
    """獲取資料"""
    return {"profiles": db.get_profiles(user['user_id'])}

@app.post("/api/record/save")
async def save_record(req: SaveRecordRequest, user: dict = Depends(require_auth)):
    """保存記錄"""
    record_type = req.record_type
    data = req.data
    
    if record_type == "bazi":
        record_id = db.save_bazi(user['user_id'], data)
    elif record_type == "ziwei":
        record_id = db.save_ziwei(user['user_id'], data)
    elif record_type == "meihua":
        record_id = db.save_meihua(user['user_id'], data)
    elif record_type == "date":
        record_id = db.save_date_selection(user['user_id'], data)
    elif record_type == "match":
        record_id = db.save_match(user['user_id'], data)
    else:
        raise HTTPException(400, f"未知記錄類型：{record_type}")
    
    return {"success": True, "record_id": record_id}

@app.get("/api/records/{record_type}")
async def get_records(record_type: str, user: dict = Depends(require_auth), limit: int = 20):
    """獲取記錄"""
    table_map = {
        "bazi": "bazi_records",
        "ziwei": "ziwei_records",
        "meihua": "meihua_records",
        "date": "date_records",
        "match": "match_records",
        "report": "report_records",
    }
    
    table = table_map.get(record_type)
    if not table:
        raise HTTPException(400, f"未知記錄類型：{record_type}")
    
    records = db.query(table, {"user_id": user['user_id']}, 
                       order_by="created_at DESC", limit=limit)
    return {"records": records}

@app.get("/api/credits")
async def get_credits(user: dict = Depends(require_auth)):
    """點數"""
    user_data = db.get_user(user['user_id'])
    logs = db.query("credit_logs", {"user_id": user['user_id']}, 
                    order_by="created_at DESC", limit=10)
    return {"credits": user_data['credits'], "logs": logs}

@app.get("/api/stats")
async def get_stats():
    """統計"""
    return db.get_stats()

@app.get("/api/db/status")
async def db_status():
    """數據庫狀態"""
    stats = db.get_stats()
    return {
        "db_path": db.db_path,
        "db_size_kb": os.path.getsize(db.db_path) // 1024 if os.path.exists(db.db_path) else 0,
        "tables": 12,
        "stats": stats,
    }


# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import tempfile
    
    print("═" * 60)
    print("        北斗命數統一數據庫 - 測試")
    print("═" * 60)
    
    # 使用臨時數據庫
    test_db = UnifiedDB(tempfile.mktemp(suffix=".db"))
    
    # 測試用戶
    print("\n【1. 用戶管理】")
    success, msg, user_id = test_db.create_user("testuser", "pass123", "test@example.com")
    print(f"  註冊：{msg} (ID={user_id})")
    
    success, user = test_db.verify_login("testuser", "pass123")
    print(f"  登入：{'✅' if success else '❌'} credits={user['credits']}")
    
    # 測試資料
    print("\n【2. 用戶資料】")
    profile_id = test_db.add_profile(user_id, {
        "name": "測試用戶",
        "gender": "男",
        "birth_year": 1990,
        "birth_month": 5,
        "birth_day": 15,
        "birth_hour": 10,
        "is_primary": 1,
    })
    print(f"  添加資料：profile_id={profile_id}")
    
    profiles = test_db.get_profiles(user_id)
    print(f"  資料數量：{len(profiles)}")
    
    # 測試命理記錄
    print("\n【3. 命理記錄】")
    bazi_id = test_db.save_bazi(user_id, {
        "year_gz": "庚午",
        "month_gz": "辛巳",
        "day_gz": "甲子",
        "hour_gz": "乙巳",
        "day_master": "甲",
        "yongshen": "水",
    })
    print(f"  八字記錄：#{bazi_id}")
    
    ziwei_id = test_db.save_ziwei(user_id, {
        "ju_shu": 5,
        "ming_gong": "子女",
        "ming_gong_idx": 3,
    })
    print(f"  紫微記錄：#{ziwei_id}")
    
    # 測試點數
    print("\n【4. 點數管理】")
    success, credits = test_db.update_credits(user_id, -30, "use", "測試扣除")
    print(f"  扣除 30 點：剩餘 {credits}")
    
    success, credits = test_db.update_credits(user_id, 50, "bonus", "測試獎勵")
    print(f"  增加 50 點：剩餘 {credits}")
    
    # 測試訂單
    print("\n【5. 訂單管理】")
    order_id = test_db.create_order(user_id, "BD20260217001", "L1", "入門版", 2800)
    print(f"  創建訂單：#{order_id}")
    
    test_db.complete_order("BD20260217001", "ECPAY123", 50)
    user = test_db.get_user(user_id)
    print(f"  完成訂單：credits={user['credits']}")
    
    # 統計
    print("\n【6. 統計】")
    stats = test_db.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    # 清理
    os.remove(test_db.db_path)
    
    print("\n" + "═" * 60)
    print("✅ 統一數據庫測試完成")
    print("═" * 60)
    print("\n啟動：uvicorn db_unified:app --port 8005")
