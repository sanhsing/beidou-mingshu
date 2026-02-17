#!/usr/bin/env python3
"""
feedback_system.py - 內測回饋系統
北斗命數 v3.1.1

功能：
1. 回饋表單 Schema
2. SQLite 存儲
3. 統計分析

GPT 建議的 3 個關鍵問題：
1. 你今天最有感的一句話是什麼？
2. 有沒有哪個部分讓你第一次用不同角度理解自己？
3. 如果今天的內容可以改進，你覺得哪裡最模糊？

內測成功標準：
- 至少 6 人能重述你的模型
- 至少 4 人說想再談一次
- 至少 3 人主動問是否可以推薦

@星殼 × @流祇
"""

import sqlite3
import json
import uuid
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

# ============================================================
# L0: 常量定義
# ============================================================

FEEDBACK_DB_PATH = os.environ.get("FEEDBACK_DB_PATH", "./feedback.db")

# 回饋問題
FEEDBACK_QUESTIONS = {
    "q1": {
        "id": "most_impactful",
        "question": "你今天最有感的一句話是什麼？",
        "purpose": "測試模型是否留下記憶點、語氣是否有力量",
        "type": "text",
    },
    "q2": {
        "id": "new_perspective",
        "question": "有沒有哪個部分讓你第一次用不同角度理解自己？",
        "purpose": "測試結構是否產生新認知",
        "type": "text",
    },
    "q3": {
        "id": "improvement",
        "question": "如果今天的內容可以改進，你覺得哪裡最模糊？",
        "purpose": "測試抽象度、語言清晰度",
        "type": "text",
    },
}

# 額外收集（可選）
OPTIONAL_QUESTIONS = {
    "would_return": {
        "question": "你是否願意再談一次？",
        "type": "choice",
        "options": ["非常願意", "願意", "考慮中", "不需要"],
    },
    "would_recommend": {
        "question": "你是否願意推薦給朋友？",
        "type": "choice",
        "options": ["非常願意", "願意", "考慮中", "不會"],
    },
    "overall_rating": {
        "question": "整體滿意度（1-5）",
        "type": "rating",
        "min": 1,
        "max": 5,
    },
}

# ============================================================
# L1: 資料結構
# ============================================================

@dataclass
class FeedbackEntry:
    """回饋條目"""
    id: str = ""
    session_id: str = ""           # 諮詢 session ID
    client_name: str = ""          # 客戶名稱（可匿名）
    service_level: str = ""        # L1/L2/L3/L4
    consultant_id: str = ""        # 顧問 ID
    
    # 核心 3 問
    most_impactful: str = ""       # Q1: 最有感的一句話
    new_perspective: str = ""      # Q2: 新角度理解
    improvement: str = ""          # Q3: 最模糊的部分
    
    # 可選問題
    would_return: str = ""         # 是否再談
    would_recommend: str = ""      # 是否推薦
    overall_rating: int = 0        # 整體評分
    
    # 元數據
    created_at: str = ""
    client_ip: str = ""
    user_agent: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

# ============================================================
# L2: 資料庫操作
# ============================================================

def get_db_connection(db_path: str = None) -> sqlite3.Connection:
    """取得資料庫連接"""
    path = db_path or FEEDBACK_DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_feedback_db(db_path: str = None) -> bool:
    """初始化回饋資料庫"""
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        # 創建回饋表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                client_name TEXT,
                service_level TEXT,
                consultant_id TEXT,
                
                most_impactful TEXT,
                new_perspective TEXT,
                improvement TEXT,
                
                would_return TEXT,
                would_recommend TEXT,
                overall_rating INTEGER,
                
                created_at TEXT,
                client_ip TEXT,
                user_agent TEXT
            )
        """)
        
        # 創建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_created 
            ON feedback(created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_service 
            ON feedback(service_level)
        """)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"初始化失敗: {e}")
        return False

def save_feedback(feedback: FeedbackEntry, db_path: str = None) -> bool:
    """儲存回饋"""
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO feedback (
                id, session_id, client_name, service_level, consultant_id,
                most_impactful, new_perspective, improvement,
                would_return, would_recommend, overall_rating,
                created_at, client_ip, user_agent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            feedback.id,
            feedback.session_id,
            feedback.client_name,
            feedback.service_level,
            feedback.consultant_id,
            feedback.most_impactful,
            feedback.new_perspective,
            feedback.improvement,
            feedback.would_return,
            feedback.would_recommend,
            feedback.overall_rating,
            feedback.created_at,
            feedback.client_ip,
            feedback.user_agent,
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"儲存失敗: {e}")
        return False

def get_all_feedback(db_path: str = None, limit: int = 100) -> List[Dict]:
    """取得所有回饋"""
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM feedback 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"查詢失敗: {e}")
        return []

def get_feedback_stats(db_path: str = None) -> Dict:
    """取得回饋統計"""
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        # 總數
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total = cursor.fetchone()[0]
        
        # 願意再談
        cursor.execute("""
            SELECT would_return, COUNT(*) 
            FROM feedback 
            WHERE would_return != ''
            GROUP BY would_return
        """)
        return_stats = dict(cursor.fetchall())
        
        # 願意推薦
        cursor.execute("""
            SELECT would_recommend, COUNT(*) 
            FROM feedback 
            WHERE would_recommend != ''
            GROUP BY would_recommend
        """)
        recommend_stats = dict(cursor.fetchall())
        
        # 平均評分
        cursor.execute("""
            SELECT AVG(overall_rating) 
            FROM feedback 
            WHERE overall_rating > 0
        """)
        avg_rating = cursor.fetchone()[0] or 0
        
        # 按服務級別
        cursor.execute("""
            SELECT service_level, COUNT(*) 
            FROM feedback 
            WHERE service_level != ''
            GROUP BY service_level
        """)
        level_stats = dict(cursor.fetchall())
        
        conn.close()
        
        # 計算內測成功指標
        would_return_positive = (
            return_stats.get("非常願意", 0) + 
            return_stats.get("願意", 0)
        )
        would_recommend_positive = (
            recommend_stats.get("非常願意", 0) + 
            recommend_stats.get("願意", 0)
        )
        
        return {
            "total": total,
            "would_return": return_stats,
            "would_recommend": recommend_stats,
            "avg_rating": round(avg_rating, 2),
            "by_level": level_stats,
            "success_metrics": {
                "would_return_count": would_return_positive,
                "would_recommend_count": would_recommend_positive,
                "target_return": 4,      # 目標：至少 4 人說想再談
                "target_recommend": 3,   # 目標：至少 3 人願意推薦
            }
        }
    except Exception as e:
        print(f"統計失敗: {e}")
        return {}

# ============================================================
# L3: 回饋分析
# ============================================================

def analyze_feedback_keywords(db_path: str = None) -> Dict:
    """分析回饋關鍵詞"""
    feedbacks = get_all_feedback(db_path)
    
    # 收集所有文字回答
    impactful_texts = [f["most_impactful"] for f in feedbacks if f.get("most_impactful")]
    perspective_texts = [f["new_perspective"] for f in feedbacks if f.get("new_perspective")]
    improvement_texts = [f["improvement"] for f in feedbacks if f.get("improvement")]
    
    return {
        "impactful_count": len(impactful_texts),
        "perspective_count": len(perspective_texts),
        "improvement_count": len(improvement_texts),
        "sample_impactful": impactful_texts[:5],
        "sample_perspective": perspective_texts[:5],
        "sample_improvement": improvement_texts[:5],
    }

def generate_feedback_report(db_path: str = None) -> str:
    """生成回饋報告"""
    stats = get_feedback_stats(db_path)
    keywords = analyze_feedback_keywords(db_path)
    
    success = stats.get("success_metrics", {})
    
    report = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    內測回饋統計報告                               ║
╚══════════════════════════════════════════════════════════════════╝

  📊 基本統計
  ─────────────────────────────────────────────────────────────────
  總回饋數：{stats.get('total', 0)}
  平均評分：{stats.get('avg_rating', 0)}/5

  📈 成功指標
  ─────────────────────────────────────────────────────────────────
  願意再談：{success.get('would_return_count', 0)}/{success.get('target_return', 4)} 人
  願意推薦：{success.get('would_recommend_count', 0)}/{success.get('target_recommend', 3)} 人

  💬 核心回饋
  ─────────────────────────────────────────────────────────────────
  最有感的話：{keywords.get('impactful_count', 0)} 條
  新角度理解：{keywords.get('perspective_count', 0)} 條
  改進建議：{keywords.get('improvement_count', 0)} 條

  📝 樣本回饋
  ─────────────────────────────────────────────────────────────────
"""
    
    for i, text in enumerate(keywords.get("sample_impactful", [])[:3], 1):
        report += f"  Q1-{i}: {text[:50]}...\n" if len(text) > 50 else f"  Q1-{i}: {text}\n"
    
    report += "\n"
    
    for i, text in enumerate(keywords.get("sample_improvement", [])[:3], 1):
        report += f"  Q3-{i}: {text[:50]}...\n" if len(text) > 50 else f"  Q3-{i}: {text}\n"
    
    report += f"""
  ─────────────────────────────────────────────────────────────────
  生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}
  ─────────────────────────────────────────────────────────────────
"""
    
    return report

# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    print("=== 回饋系統測試 ===\n")
    
    # 初始化
    init_feedback_db("/tmp/test_feedback.db")
    print("✅ 資料庫初始化成功")
    
    # 測試儲存
    test_feedback = FeedbackEntry(
        session_id="test-001",
        client_name="測試用戶",
        service_level="L2",
        most_impactful="結構決定阻力，人決定方向",
        new_perspective="原來我一直在用土的能量壓制自己",
        improvement="五行圖可以更直觀一些",
        would_return="非常願意",
        would_recommend="願意",
        overall_rating=5,
    )
    
    save_feedback(test_feedback, "/tmp/test_feedback.db")
    print("✅ 回饋儲存成功")
    
    # 測試查詢
    all_fb = get_all_feedback("/tmp/test_feedback.db")
    print(f"✅ 查詢成功，共 {len(all_fb)} 條")
    
    # 測試統計
    stats = get_feedback_stats("/tmp/test_feedback.db")
    print(f"✅ 統計成功：{stats}")
    
    # 生成報告
    report = generate_feedback_report("/tmp/test_feedback.db")
    print(report)
