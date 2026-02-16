"""
北斗命數資料庫 Schema mingshu_schema.py v1.0
==========================================
XTF任務：消-D1 | 執行星：星殼（架構）+ 流祇（連結）
確定度：★★★★★（結構設計確定）

核心本質：Schema = 用戶 + 命盤 + 報告 + 查詢歷史

📚 資料庫設計原則：
1. 九庫架構對接（meta 為主）
2. 三層分離（事實/模型/解讀）
3. 可追溯（版本控制）
4. 可擴展（預留欄位）
"""

import sqlite3
from typing import Optional
from datetime import datetime

# ============================================================
# Schema 定義（SQL）
# ============================================================

MINGSHU_SCHEMA = """
-- ============================================================
-- 北斗命數資料庫 Schema v1.0
-- 建立日期：2026-02-07
-- 九庫對接：meta_toolkit.db
-- ============================================================

-- 用戶表
CREATE TABLE IF NOT EXISTS ms_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    name TEXT,
    gender TEXT CHECK(gender IN ('男', '女')),
    birth_year INTEGER,
    birth_month INTEGER,
    birth_day INTEGER,
    birth_hour INTEGER,
    is_lunar INTEGER DEFAULT 0,
    leap_month INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT DEFAULT (datetime('now', 'localtime'))
);

-- 八字命盤表
CREATE TABLE IF NOT EXISTS ms_bazi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    year_gan TEXT, year_zhi TEXT,
    month_gan TEXT, month_zhi TEXT,
    day_gan TEXT, day_zhi TEXT,
    hour_gan TEXT, hour_zhi TEXT,
    day_master TEXT, day_master_wx TEXT,
    strength_score INTEGER, strength_level TEXT,
    yongshen TEXT, xishen TEXT, jishen TEXT,
    geju_name TEXT, geju_field TEXT,
    wx_mu INTEGER DEFAULT 0, wx_huo INTEGER DEFAULT 0,
    wx_tu INTEGER DEFAULT 0, wx_jin INTEGER DEFAULT 0, wx_shui INTEGER DEFAULT 0,
    calc_version TEXT DEFAULT '2.3',
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES ms_users(id)
);

-- 紫微命盤表
CREATE TABLE IF NOT EXISTS ms_ziwei (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ju_shu TEXT, ming_gong TEXT, ming_gong_idx INTEGER,
    shen_gong TEXT, shen_gong_idx INTEGER,
    ming_stars TEXT, shen_stars TEXT,
    sihua_lu TEXT, sihua_quan TEXT, sihua_ke TEXT, sihua_ji TEXT,
    gongs_data TEXT,
    calc_version TEXT DEFAULT '2.3',
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES ms_users(id)
);

-- 八字大運表
CREATE TABLE IF NOT EXISTS ms_bazi_dayun (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bazi_id INTEGER,
    direction TEXT, qiyun_age REAL,
    dayun_list TEXT,
    calc_version TEXT DEFAULT '2.3',
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES ms_users(id)
);

-- 紫微大限表
CREATE TABLE IF NOT EXISTS ms_ziwei_daxian (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ziwei_id INTEGER,
    direction TEXT, start_age INTEGER,
    daxian_list TEXT,
    calc_version TEXT DEFAULT '2.3',
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES ms_users(id)
);

-- 流年分析表
CREATE TABLE IF NOT EXISTS ms_liunian (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    ganzhi TEXT, gan TEXT, zhi TEXT,
    bazi_gan_shishen TEXT, bazi_tendency TEXT, bazi_advice TEXT,
    ziwei_taisui_gong TEXT, ziwei_sihua TEXT,
    overall_tendency TEXT, overall_advice TEXT,
    certainty TEXT DEFAULT '★★★☆☆',
    calc_version TEXT DEFAULT '2.3',
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES ms_users(id),
    UNIQUE(user_id, year)
);

-- 完整報告表
CREATE TABLE IF NOT EXISTS ms_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    report_type TEXT, report_version TEXT, report_content TEXT,
    params TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES ms_users(id)
);

-- 查詢歷史表
CREATE TABLE IF NOT EXISTS ms_query_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    query_type TEXT, query_params TEXT, result_summary TEXT,
    ip_address TEXT, user_agent TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

-- 神煞記錄表
CREATE TABLE IF NOT EXISTS ms_shensha (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bazi_id INTEGER,
    shensha_name TEXT, shensha_category TEXT,
    found_in TEXT, vernacular TEXT, field_theory TEXT, advice TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES ms_users(id)
);

-- 框架版本表
CREATE TABLE IF NOT EXISTS ms_framework_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_name TEXT UNIQUE, version TEXT, description TEXT,
    updated_at TEXT DEFAULT (datetime('now', 'localtime'))
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_users_uuid ON ms_users(uuid);
CREATE INDEX IF NOT EXISTS idx_bazi_user ON ms_bazi(user_id);
CREATE INDEX IF NOT EXISTS idx_ziwei_user ON ms_ziwei(user_id);
CREATE INDEX IF NOT EXISTS idx_liunian_user_year ON ms_liunian(user_id, year);
CREATE INDEX IF NOT EXISTS idx_reports_user ON ms_reports(user_id);

-- 初始資料
INSERT OR IGNORE INTO ms_framework_versions (module_name, version, description) VALUES
    ('field_translation', '2.0', '場論翻譯系統'),
    ('wuxing_analyzer', '1.0', '五行強弱分析'),
    ('geju_analyzer', '1.0', '格局判斷'),
    ('sihua_translation', '1.0', '四化詳解'),
    ('shensha_translation', '1.0', '神煞白話'),
    ('dayun_calculator', '1.0', '八字大運計算'),
    ('daxian_calculator', '1.0', '紫微大限計算'),
    ('liunian_analyzer', '1.0', '流年分析');
"""

def init_mingshu_db(db_path: str = "mingshu.db") -> sqlite3.Connection:
    """初始化命數資料庫"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(MINGSHU_SCHEMA)
    conn.commit()
    return conn

def get_schema_info(conn: sqlite3.Connection) -> dict:
    """取得 Schema 資訊"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ms_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    table_info = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        table_info[table] = {"column_count": len(columns), "columns": [col[1] for col in columns]}
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
    indexes = [row[0] for row in cursor.fetchall()]
    
    return {"tables": tables, "table_count": len(tables), "table_info": table_info, "indexes": indexes}

if __name__ == "__main__":
    conn = init_mingshu_db("test_mingshu.db")
    info = get_schema_info(conn)
    print(f"北斗命數 Schema v1.0 | 表：{info['table_count']} | 索引：{len(info['indexes'])}")
    conn.close()
    import os; os.remove("test_mingshu.db")
