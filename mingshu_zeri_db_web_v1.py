#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mingshu_zeri_db_web_v1.py - 北斗命數擇日+存儲+Web v1.0
=======================================================
北斗七星文創 × 織明

XTF⁸ 任務鏈：M7+M8+M9
執行星：織明(設計) × 理樞(整合) × 星殼(架構) × 璃語(界面)

模組整合：
    M7: ZeriEngine    - 擇日擇時 (活動時機選擇)
    M8: MingshuDB     - 命盤存儲 (SQLite持久化)
    M9: MingshuWeb    - Web界面 (Flask API)

依賴：
    - mingshu_engine_v1.py (統一命數引擎)
    - mingshu_liunian_hepan_v1.py (流年合盤)
    - PYLIB: mingshu_db, qimen_engine_v1

📚 知識點：
    「擇日即擇場」：選擇最佳場態時機
    「命盤持久化」：場態的時間切片存儲
    「Web即橋樑」：人機協作界面
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any, Callable
from enum import Enum
from datetime import datetime, date, timedelta
import sqlite3
import json
import os

# 導入本地模組
try:
    from mingshu_engine_v1 import (
        MingshuEngine, MingshuResult, BirthInfo, BaziChart,
        FieldState, Gender, CalendarType, TIANGAN, DIZHI, WUXING,
        TIANGAN_WUXING, DIZHI_WUXING
    )
    from mingshu_liunian_hepan_v1 import LiunianEngine, HepanEngine
except ImportError:
    TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    WUXING = ["木", "火", "土", "金", "水"]
    TIANGAN_WUXING = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
        "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
    }
    DIZHI_WUXING = {
        "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
        "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
    }


# =============================================================================
# 共用常量與枚舉
# =============================================================================

class ActivityType(Enum):
    """活動類型"""
    GENERAL = "通用"
    BUSINESS = "商業"       # 開業、簽約、談判
    MARRIAGE = "婚姻"       # 結婚、訂婚
    TRAVEL = "出行"         # 旅行、搬遷
    HEALTH = "醫療"         # 手術、看診
    STUDY = "學習"          # 考試、入學
    MEETING = "會議"        # 重要會議
    INVEST = "投資"         # 投資決策
    LAUNCH = "發布"         # 產品發布、上線


class TimeQuality(Enum):
    """時辰品質"""
    EXCELLENT = "大吉"
    GOOD = "吉"
    NEUTRAL = "平"
    AVOID = "忌"
    BAD = "凶"


# 活動對應的有利十神
ACTIVITY_FAVORABLE = {
    ActivityType.GENERAL: ["比劫", "印星", "食傷"],
    ActivityType.BUSINESS: ["財星", "食傷"],
    ActivityType.MARRIAGE: ["財星", "官殺"],
    ActivityType.TRAVEL: ["食傷", "財星"],
    ActivityType.HEALTH: ["印星", "比劫"],
    ActivityType.STUDY: ["印星", "食傷"],
    ActivityType.MEETING: ["官殺", "印星"],
    ActivityType.INVEST: ["財星", "食傷"],
    ActivityType.LAUNCH: ["食傷", "財星"],
}

# 時辰對應（簡化）
HOUR_TO_DIZHI = {
    (23, 1): "子", (1, 3): "丑", (3, 5): "寅", (5, 7): "卯",
    (7, 9): "辰", (9, 11): "巳", (11, 13): "午", (13, 15): "未",
    (15, 17): "申", (17, 19): "酉", (19, 21): "戌", (21, 23): "亥"
}


# =============================================================================
# M7: 擇日擇時引擎
# =============================================================================

@dataclass 
class TimeSlot:
    """時間段"""
    date: date
    hour_start: int
    hour_end: int
    dizhi: str
    quality: TimeQuality
    score: float
    reasons: List[str]
    field_state: Optional['FieldState'] = None
    
    def to_dict(self) -> Dict:
        return {
            "date": self.date.isoformat(),
            "hour_start": self.hour_start,
            "hour_end": self.hour_end,
            "time_range": f"{self.hour_start:02d}:00-{self.hour_end:02d}:00",
            "dizhi": self.dizhi,
            "quality": self.quality.value,
            "score": round(self.score, 1),
            "reasons": self.reasons,
            "field_score": self.field_state.field_score if self.field_state else None
        }


@dataclass
class ZeriResult:
    """擇日結果"""
    birth_info: 'BirthInfo'
    activity: ActivityType
    date_range: Tuple[date, date]
    best_times: List[TimeSlot]
    good_times: List[TimeSlot]
    avoid_times: List[TimeSlot]
    summary: str
    
    def to_dict(self) -> Dict:
        return {
            "activity": self.activity.value,
            "date_range": [self.date_range[0].isoformat(), self.date_range[1].isoformat()],
            "best_times": [t.to_dict() for t in self.best_times[:5]],
            "good_times": [t.to_dict() for t in self.good_times[:10]],
            "avoid_times": [t.to_dict() for t in self.avoid_times[:5]],
            "summary": self.summary
        }


@dataclass
class FieldState:
    """場態（簡化版）"""
    coherence: float = 0.0
    friction: float = 0.0
    volatility: float = 0.0
    sustainability: float = 0.5
    triggers: List[str] = field(default_factory=list)
    
    @property
    def field_score(self) -> float:
        base = (self.coherence + 1) / 2 * 40
        friction_penalty = self.friction * 20
        volatility_penalty = self.volatility * 20
        sustain_bonus = self.sustainability * 20
        return max(0, min(100, base - friction_penalty - volatility_penalty + sustain_bonus))
    
    def to_dict(self) -> Dict:
        return {
            "coherence": round(self.coherence, 3),
            "friction": round(self.friction, 3),
            "volatility": round(self.volatility, 3),
            "sustainability": round(self.sustainability, 3),
            "field_score": round(self.field_score, 1)
        }


class ZeriEngine:
    """
    擇日擇時引擎
    
    M7: 活動類型 + 時間範圍 → 最佳時機
    
    📚 知識點：
        擇日 = 擇場
        時辰 = 場的微觀切片
        吉時 = 場態與活動共振
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        try:
            self.engine = MingshuEngine()
            self.liunian = LiunianEngine()
        except:
            self.engine = None
            self.liunian = None
    
    def _get_hour_dizhi(self, hour: int) -> str:
        """獲取時辰地支"""
        for (h_start, h_end), dz in HOUR_TO_DIZHI.items():
            if h_start <= hour < h_end or (h_start == 23 and (hour >= 23 or hour < 1)):
                return dz
        return "子"
    
    def _calc_day_ganzhi(self, dt: date) -> Tuple[str, str]:
        """日干支計算"""
        year, month, day = dt.year, dt.month, dt.day
        if month <= 2:
            year -= 1
            month += 12
        
        a = year // 100
        b = 2 - a + a // 4
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524
        
        base_jd = 2445336
        diff = jd - base_jd
        idx = diff % 60
        if idx < 0:
            idx += 60
        
        return (TIANGAN[idx % 10], DIZHI[idx % 12])
    
    def _calc_hour_ganzhi(self, day_gan: str, hour: int) -> Tuple[str, str]:
        """時干支計算"""
        dizhi = self._get_hour_dizhi(hour)
        zhi_idx = DIZHI.index(dizhi)
        day_gan_idx = TIANGAN.index(day_gan)
        
        base_gan = {0: 0, 1: 0, 2: 2, 3: 2, 4: 4, 5: 4, 6: 6, 7: 6, 8: 8, 9: 8}
        hour_gan_base = base_gan.get(day_gan_idx, 0)
        gan_idx = (hour_gan_base + zhi_idx) % 10
        
        return (TIANGAN[gan_idx], dizhi)
    
    def _get_relation(self, day_master_wx: str, target_wx: str) -> str:
        """獲取十神關係"""
        WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
        
        if day_master_wx == target_wx:
            return "比劫"
        if WUXING_SHENG.get(day_master_wx) == target_wx:
            return "食傷"
        if WUXING_KE.get(day_master_wx) == target_wx:
            return "財星"
        if WUXING_KE.get(target_wx) == day_master_wx:
            return "官殺"
        if WUXING_SHENG.get(target_wx) == day_master_wx:
            return "印星"
        return "中性"
    
    def _evaluate_time_slot(
        self,
        birth_info: 'BirthInfo',
        day_master_wx: str,
        target_date: date,
        hour: int,
        activity: ActivityType
    ) -> TimeSlot:
        """評估單個時間段"""
        # 計算干支
        day_gan, day_zhi = self._calc_day_ganzhi(target_date)
        hour_gan, hour_zhi = self._calc_hour_ganzhi(day_gan, hour)
        
        # 計算五行關係
        hour_gan_wx = TIANGAN_WUXING.get(hour_gan, "")
        hour_zhi_wx = DIZHI_WUXING.get(hour_zhi, "")
        day_gan_wx = TIANGAN_WUXING.get(day_gan, "")
        
        # 與日主關係
        gan_relation = self._get_relation(day_master_wx, hour_gan_wx)
        zhi_relation = self._get_relation(day_master_wx, hour_zhi_wx)
        
        # 評分
        favorable = ACTIVITY_FAVORABLE.get(activity, ["比劫", "印星"])
        score = 50.0
        reasons = []
        
        # 時干評分
        if gan_relation in favorable:
            score += 20
            reasons.append(f"時干{hour_gan}({gan_relation})有利")
        elif gan_relation in ["官殺"]:
            score -= 15
            reasons.append(f"時干{hour_gan}({gan_relation})有壓力")
        
        # 時支評分
        if zhi_relation in favorable:
            score += 15
            reasons.append(f"時支{hour_zhi}({zhi_relation})助力")
        elif zhi_relation in ["官殺"]:
            score -= 10
        
        # 日支評分（簡化）
        day_zhi_wx = DIZHI_WUXING.get(day_zhi, "")
        day_relation = self._get_relation(day_master_wx, day_zhi_wx)
        if day_relation in favorable:
            score += 10
            reasons.append(f"日支{day_zhi}配合")
        
        # 特殊時辰（簡化）
        good_hours = ["辰", "巳", "午", "未"]  # 陽氣旺
        if hour_zhi in good_hours:
            score += 5
            reasons.append("陽氣旺時")
        
        # 計算場態
        coherence = (score - 50) / 50
        volatility = 0.3 if hour_zhi in ["子", "卯", "午", "酉"] else 0.2
        
        field_state = FieldState(
            coherence=max(-1, min(1, coherence)),
            friction=0.3 if gan_relation == "官殺" else 0.1,
            volatility=volatility,
            sustainability=0.6 if zhi_relation in ["印星", "比劫"] else 0.4,
            triggers=[f"{hour_gan}{hour_zhi}", gan_relation]
        )
        
        # 判斷品質
        if score >= 80:
            quality = TimeQuality.EXCELLENT
        elif score >= 65:
            quality = TimeQuality.GOOD
        elif score >= 45:
            quality = TimeQuality.NEUTRAL
        elif score >= 30:
            quality = TimeQuality.AVOID
        else:
            quality = TimeQuality.BAD
        
        # 時間範圍
        hour_end = (hour + 2) % 24
        if hour_end == 0:
            hour_end = 24
        
        return TimeSlot(
            date=target_date,
            hour_start=hour,
            hour_end=hour_end,
            dizhi=hour_zhi,
            quality=quality,
            score=score,
            reasons=reasons if reasons else [f"{hour_gan}{hour_zhi}時"],
            field_state=field_state
        )
    
    def analyze(
        self,
        birth_info: 'BirthInfo',
        activity: ActivityType = ActivityType.GENERAL,
        start_date: date = None,
        days: int = 7
    ) -> ZeriResult:
        """
        擇日分析
        
        📚 知識點：
            擇日 = 選擇場態與活動共振的時機
        """
        if start_date is None:
            start_date = date.today()
        
        end_date = start_date + timedelta(days=days)
        
        # 獲取日主
        if self.engine:
            bazi = self.engine.get_bazi(birth_info)
            day_master = bazi.day_master
        else:
            day_master = "甲"
        
        day_master_wx = TIANGAN_WUXING.get(day_master, "木")
        
        # 評估所有時間段
        all_slots = []
        current = start_date
        
        while current <= end_date:
            for hour in range(0, 24, 2):  # 每兩小時一個時辰
                slot = self._evaluate_time_slot(
                    birth_info, day_master_wx, current, hour, activity
                )
                all_slots.append(slot)
            current += timedelta(days=1)
        
        # 分類
        best = [s for s in all_slots if s.quality == TimeQuality.EXCELLENT]
        good = [s for s in all_slots if s.quality == TimeQuality.GOOD]
        avoid = [s for s in all_slots if s.quality in [TimeQuality.AVOID, TimeQuality.BAD]]
        
        # 排序
        best.sort(key=lambda x: -x.score)
        good.sort(key=lambda x: -x.score)
        avoid.sort(key=lambda x: x.score)
        
        # 生成摘要
        if best:
            summary = f"未來{days}天有{len(best)}個大吉時段，首選：{best[0].date} {best[0].hour_start}:00"
        elif good:
            summary = f"未來{days}天有{len(good)}個吉時段，建議：{good[0].date} {good[0].hour_start}:00"
        else:
            summary = f"未來{days}天時機一般，建議擇日再議"
        
        return ZeriResult(
            birth_info=birth_info,
            activity=activity,
            date_range=(start_date, end_date),
            best_times=best,
            good_times=good,
            avoid_times=avoid,
            summary=summary
        )


# =============================================================================
# M8: 命盤存儲引擎
# =============================================================================

class MingshuDB:
    """
    命盤存儲引擎
    
    M8: MingshuResult → SQLite 持久化
    
    📚 知識點：
        存儲 = 場態的時間切片凝固
        檢索 = 場態的歷史回溯
    """
    
    VERSION = "1.0.0"
    DB_NAME = "mingshu_data.db"
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or self.DB_NAME
        self._init_db()
    
    def _init_db(self):
        """初始化資料庫"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 用戶表
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                birth_year INTEGER,
                birth_month INTEGER,
                birth_day INTEGER,
                birth_hour INTEGER,
                gender TEXT,
                calendar TEXT DEFAULT 'lunar',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 命盤表
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                chart_type TEXT,
                bazi_string TEXT,
                day_master TEXT,
                field_score REAL,
                full_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # 查詢記錄表
        cur.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                query_type TEXT,
                query_params TEXT,
                result_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # 索引
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_name ON users(name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_charts_user ON charts(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_queries_user ON queries(user_id)")
        
        conn.commit()
        conn.close()
    
    def save_user(self, birth_info: 'BirthInfo') -> int:
        """保存用戶"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 檢查是否存在
        cur.execute("""
            SELECT id FROM users 
            WHERE name = ? AND birth_year = ? AND birth_month = ? AND birth_day = ?
        """, (
            birth_info.name if hasattr(birth_info, 'name') else "",
            birth_info.year,
            birth_info.month,
            birth_info.day
        ))
        
        row = cur.fetchone()
        if row:
            user_id = row[0]
        else:
            cur.execute("""
                INSERT INTO users (name, birth_year, birth_month, birth_day, birth_hour, gender, calendar)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                birth_info.name if hasattr(birth_info, 'name') else "",
                birth_info.year,
                birth_info.month,
                birth_info.day,
                birth_info.hour,
                birth_info.gender.value if hasattr(birth_info, 'gender') else "M",
                birth_info.calendar.value if hasattr(birth_info, 'calendar') else "lunar"
            ))
            user_id = cur.lastrowid
        
        conn.commit()
        conn.close()
        return user_id
    
    def save_chart(self, user_id: int, result: 'MingshuResult') -> int:
        """保存命盤"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        bazi_string = result.bazi.bazi_string if result.bazi else ""
        day_master = result.bazi.day_master if result.bazi else ""
        field_score = result.field_state.field_score if result.field_state else 0
        
        full_data = json.dumps(result.to_dict(), ensure_ascii=False)
        
        cur.execute("""
            INSERT INTO charts (user_id, chart_type, bazi_string, day_master, field_score, full_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, "full", bazi_string, day_master, field_score, full_data))
        
        chart_id = cur.lastrowid
        conn.commit()
        conn.close()
        return chart_id
    
    def save_result(self, birth_info: 'BirthInfo', result: 'MingshuResult') -> Tuple[int, int]:
        """保存完整結果（用戶+命盤）"""
        user_id = self.save_user(birth_info)
        chart_id = self.save_chart(user_id, result)
        return (user_id, chart_id)
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """獲取用戶"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "birth_year": row[2],
                "birth_month": row[3],
                "birth_day": row[4],
                "birth_hour": row[5],
                "gender": row[6],
                "calendar": row[7],
                "created_at": row[8]
            }
        return None
    
    def get_chart(self, chart_id: int) -> Optional[Dict]:
        """獲取命盤"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM charts WHERE id = ?", (chart_id,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "chart_type": row[2],
                "bazi_string": row[3],
                "day_master": row[4],
                "field_score": row[5],
                "full_data": json.loads(row[6]) if row[6] else None,
                "created_at": row[7]
            }
        return None
    
    def search_users(self, name: str = None, limit: int = 10) -> List[Dict]:
        """搜索用戶"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        if name:
            cur.execute(
                "SELECT * FROM users WHERE name LIKE ? ORDER BY created_at DESC LIMIT ?",
                (f"%{name}%", limit)
            )
        else:
            cur.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT ?", (limit,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "name": r[1],
            "birth_year": r[2],
            "birth_month": r[3],
            "birth_day": r[4],
            "gender": r[6]
        } for r in rows]
    
    def get_user_charts(self, user_id: int, limit: int = 10) -> List[Dict]:
        """獲取用戶所有命盤"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute(
            "SELECT id, chart_type, bazi_string, day_master, field_score, created_at FROM charts WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        
        rows = cur.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "chart_type": r[1],
            "bazi_string": r[2],
            "day_master": r[3],
            "field_score": r[4],
            "created_at": r[5]
        } for r in rows]
    
    def log_query(self, user_id: int, query_type: str, params: Dict, summary: str):
        """記錄查詢"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO queries (user_id, query_type, query_params, result_summary)
            VALUES (?, ?, ?, ?)
        """, (user_id, query_type, json.dumps(params, ensure_ascii=False), summary))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """獲取統計"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM charts")
        chart_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM queries")
        query_count = cur.fetchone()[0]
        
        conn.close()
        
        return {
            "users": user_count,
            "charts": chart_count,
            "queries": query_count,
            "db_path": self.db_path
        }


# =============================================================================
# M9: Web 界面
# =============================================================================

# HTML 模板
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>北斗命數系統</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Microsoft JhengHei', sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #eee;
        }
        h1 {
            text-align: center;
            color: #ffd700;
            text-shadow: 0 0 10px rgba(255,215,0,0.5);
        }
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h2 {
            color: #ffd700;
            margin-top: 0;
        }
        label {
            display: block;
            margin: 10px 0 5px;
            color: #ccc;
        }
        input, select {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 8px;
            background: rgba(255,255,255,0.15);
            color: #fff;
            font-size: 16px;
        }
        input:focus, select:focus {
            outline: 2px solid #ffd700;
        }
        button {
            background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
            color: #1a1a2e;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 10px 5px;
            transition: transform 0.2s;
        }
        button:hover {
            transform: scale(1.05);
        }
        .result {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            white-space: pre-wrap;
            font-family: monospace;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .tab.active, .tab:hover {
            background: #ffd700;
            color: #1a1a2e;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .stat {
            text-align: center;
            padding: 15px;
            background: rgba(255,215,0,0.1);
            border-radius: 10px;
        }
        .stat-value {
            font-size: 2em;
            color: #ffd700;
            font-weight: bold;
        }
        .stat-label {
            color: #aaa;
        }
        .api-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }
        .api-item {
            background: rgba(255,255,255,0.05);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .api-item code {
            color: #ffd700;
        }
    </style>
</head>
<body>
    <h1>🌟 北斗命數系統</h1>
    
    <div class="card">
        <h2>📋 輸入生辰</h2>
        <div class="grid">
            <div>
                <label>姓名</label>
                <input type="text" id="name" value="測試">
            </div>
            <div>
                <label>年</label>
                <input type="number" id="year" value="1983" min="1900" max="2100">
            </div>
            <div>
                <label>月</label>
                <input type="number" id="month" value="12" min="1" max="12">
            </div>
            <div>
                <label>日</label>
                <input type="number" id="day" value="16" min="1" max="31">
            </div>
            <div>
                <label>時</label>
                <input type="number" id="hour" value="5" min="0" max="23">
            </div>
            <div>
                <label>性別</label>
                <select id="gender">
                    <option value="M">男</option>
                    <option value="F">女</option>
                </select>
            </div>
            <div>
                <label>曆法</label>
                <select id="calendar">
                    <option value="lunar">農曆</option>
                    <option value="solar">陽曆</option>
                </select>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>🔮 功能選擇</h2>
        <button onclick="callAPI('bazi')">八字排盤</button>
        <button onclick="callAPI('full')">完整命盤</button>
        <button onclick="callAPI('field')">場態分析</button>
        <button onclick="callAPI('liunian')">流年運勢</button>
        <button onclick="callAPI('now')">當下起卦</button>
        <button onclick="callAPI('zeri')">擇日擇時</button>
    </div>
    
    <div class="card">
        <h2>📊 結果</h2>
        <div id="result" class="result">等待查詢...</div>
    </div>
    
    <div class="card">
        <h2>🔌 API 端點</h2>
        <div class="api-list">
            <div class="api-item"><code>/api/bazi</code><br>八字</div>
            <div class="api-item"><code>/api/ziwei</code><br>紫微</div>
            <div class="api-item"><code>/api/yijing</code><br>易經</div>
            <div class="api-item"><code>/api/full</code><br>完整</div>
            <div class="api-item"><code>/api/field</code><br>場態</div>
            <div class="api-item"><code>/api/advice</code><br>建議</div>
            <div class="api-item"><code>/api/liunian</code><br>流年</div>
            <div class="api-item"><code>/api/hepan</code><br>合盤</div>
            <div class="api-item"><code>/api/zeri</code><br>擇日</div>
            <div class="api-item"><code>/api/now</code><br>當下</div>
            <div class="api-item"><code>/api/stats</code><br>統計</div>
        </div>
    </div>
    
    <script>
        function getBirthInfo() {
            return {
                name: document.getElementById('name').value,
                year: parseInt(document.getElementById('year').value),
                month: parseInt(document.getElementById('month').value),
                day: parseInt(document.getElementById('day').value),
                hour: parseInt(document.getElementById('hour').value),
                gender: document.getElementById('gender').value,
                calendar: document.getElementById('calendar').value
            };
        }
        
        async function callAPI(endpoint) {
            const resultDiv = document.getElementById('result');
            resultDiv.textContent = '查詢中...';
            
            try {
                const response = await fetch('/api/' + endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(getBirthInfo())
                });
                const data = await response.json();
                resultDiv.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                resultDiv.textContent = '錯誤: ' + error.message;
            }
        }
    </script>
</body>
</html>"""


class MingshuWeb:
    """
    北斗命數 Web 界面
    
    M9: Flask API + HTML 界面
    
    📚 知識點：
        Web = 人機橋樑
        API = 功能暴露
        界面 = 場態可視化
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.host = host
        self.port = port
        
        # 初始化引擎
        try:
            self.engine = MingshuEngine()
            self.liunian = LiunianEngine()
            self.hepan = HepanEngine()
        except:
            self.engine = None
            self.liunian = None
            self.hepan = None
        
        self.zeri = ZeriEngine()
        self.db = MingshuDB()
        
        self.app = None
    
    def _parse_birth_info(self, data: Dict) -> 'BirthInfo':
        """解析出生資訊"""
        try:
            from mingshu_engine_v1 import BirthInfo, Gender, CalendarType
            return BirthInfo(
                year=data.get("year", 1990),
                month=data.get("month", 1),
                day=data.get("day", 1),
                hour=data.get("hour", 12),
                gender=Gender(data.get("gender", "M")),
                calendar=CalendarType(data.get("calendar", "lunar")),
                name=data.get("name", "")
            )
        except:
            class SimpleBirth:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
                def to_dict(self):
                    return self.__dict__
            return SimpleBirth(**data)
    
    def create_app(self):
        """創建 Flask 應用"""
        try:
            from flask import Flask, request, jsonify
        except ImportError:
            print("Flask 未安裝，請執行: pip install flask")
            return None
        
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            return HTML_TEMPLATE
        
        @app.route('/api/bazi', methods=['POST'])
        def api_bazi():
            data = request.get_json()
            birth = self._parse_birth_info(data)
            if self.engine:
                chart = self.engine.get_bazi(birth)
                analysis = self.engine.analyze_bazi(chart)
                return jsonify({"chart": chart.to_dict(), "analysis": analysis})
            return jsonify({"error": "Engine not available"})
        
        @app.route('/api/full', methods=['POST'])
        def api_full():
            data = request.get_json()
            birth = self._parse_birth_info(data)
            if self.engine:
                result = self.engine.generate_full(birth)
                # 保存到資料庫
                user_id, chart_id = self.db.save_result(birth, result)
                response = result.to_dict()
                response["db"] = {"user_id": user_id, "chart_id": chart_id}
                return jsonify(response)
            return jsonify({"error": "Engine not available"})
        
        @app.route('/api/field', methods=['POST'])
        def api_field():
            data = request.get_json()
            birth = self._parse_birth_info(data)
            if self.engine:
                result = self.engine.generate_full(birth)
                if result.field_state:
                    return jsonify(result.field_state.to_dict())
            return jsonify({"error": "Field calculation failed"})
        
        @app.route('/api/liunian', methods=['POST'])
        def api_liunian():
            data = request.get_json()
            birth = self._parse_birth_info(data)
            if self.liunian:
                result = self.liunian.analyze(birth)
                return jsonify(result.to_dict())
            return jsonify({"error": "LiunianEngine not available"})
        
        @app.route('/api/hepan', methods=['POST'])
        def api_hepan():
            data = request.get_json()
            person_a = self._parse_birth_info(data.get("person_a", data))
            person_b = self._parse_birth_info(data.get("person_b", {}))
            if self.hepan:
                result = self.hepan.analyze(person_a, person_b)
                return jsonify(result.to_dict())
            return jsonify({"error": "HepanEngine not available"})
        
        @app.route('/api/zeri', methods=['POST'])
        def api_zeri():
            data = request.get_json()
            birth = self._parse_birth_info(data)
            activity_str = data.get("activity", "general")
            try:
                activity = ActivityType(activity_str)
            except:
                activity = ActivityType.GENERAL
            
            days = data.get("days", 7)
            result = self.zeri.analyze(birth, activity, days=days)
            return jsonify(result.to_dict())
        
        @app.route('/api/now', methods=['POST', 'GET'])
        def api_now():
            if self.engine:
                gua = self.engine.get_yijing_now()
                return jsonify(gua.to_dict())
            return jsonify({"error": "Engine not available"})
        
        @app.route('/api/stats', methods=['GET'])
        def api_stats():
            return jsonify(self.db.get_stats())
        
        @app.route('/api/users', methods=['GET'])
        def api_users():
            name = request.args.get('name')
            users = self.db.search_users(name)
            return jsonify(users)
        
        @app.route('/api/health', methods=['GET'])
        def api_health():
            return jsonify({
                "status": "healthy",
                "version": self.VERSION,
                "engines": {
                    "mingshu": self.engine is not None,
                    "liunian": self.liunian is not None,
                    "hepan": self.hepan is not None,
                    "zeri": True,
                    "db": True
                }
            })
        
        self.app = app
        return app
    
    def run(self):
        """啟動服務"""
        app = self.create_app()
        if app:
            print(f"🌟 北斗命數系統啟動中...")
            print(f"📍 http://{self.host}:{self.port}")
            app.run(host=self.host, port=self.port, debug=True)
        else:
            print("無法啟動服務，請安裝 Flask: pip install flask")


# =============================================================================
# CLI 入口
# =============================================================================

def main():
    """CLI 入口"""
    print("=" * 60)
    print("北斗命數 擇日+存儲+Web v1.0")
    print("M7 (擇日) + M8 (存儲) + M9 (Web)")
    print("=" * 60)
    
    # 測試 M7
    print("\n【M7 擇日擇時】")
    zeri = ZeriEngine()
    
    try:
        from mingshu_engine_v1 import BirthInfo, Gender, CalendarType
        birth = BirthInfo(
            year=1983, month=12, day=16, hour=5,
            gender=Gender.MALE, calendar=CalendarType.LUNAR, name="北斗"
        )
    except:
        class SimpleBirth:
            def __init__(self):
                self.year, self.month, self.day, self.hour = 1983, 12, 16, 5
                self.name = "北斗"
                self.gender = type('', (), {'value': 'M'})()
                self.calendar = type('', (), {'value': 'lunar'})()
        birth = SimpleBirth()
    
    result = zeri.analyze(birth, ActivityType.BUSINESS, days=3)
    print(f"  活動: {result.activity.value}")
    print(f"  日期範圍: {result.date_range[0]} ~ {result.date_range[1]}")
    print(f"  大吉時段: {len(result.best_times)} 個")
    print(f"  吉時段: {len(result.good_times)} 個")
    print(f"  摘要: {result.summary}")
    
    if result.best_times:
        best = result.best_times[0]
        print(f"  最佳: {best.date} {best.hour_start}:00 ({best.quality.value}) - {best.reasons}")
    
    # 測試 M8
    print("\n【M8 命盤存儲】")
    db = MingshuDB("test_mingshu.db")
    
    # 保存用戶
    user_id = db.save_user(birth)
    print(f"  用戶ID: {user_id}")
    
    # 獲取統計
    stats = db.get_stats()
    print(f"  統計: {stats}")
    
    # 搜索用戶
    users = db.search_users("北斗")
    print(f"  搜索結果: {len(users)} 條")
    
    # 測試 M9
    print("\n【M9 Web界面】")
    web = MingshuWeb()
    print(f"  版本: {web.VERSION}")
    print(f"  資料庫: {web.db.get_stats()}")
    
    print("\n  啟動命令: python mingshu_zeri_db_web_v1.py --serve")
    
    print("\n" + "=" * 60)
    print("擇日即擇場，存儲即凝固，Web即橋樑")
    print("=" * 60)
    
    # 命令行參數
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--serve":
        web.run()


if __name__ == "__main__":
    main()


# =============================================================================
# 📚 知識點總結
# =============================================================================
"""
【M7 擇日擇時】

擇日公式：
- 吉時 = 時辰場態 ∩ 活動需求
- 評分 = 時干關係 + 時支關係 + 日支配合

活動類型映射：
- 商業 → 財星/食傷
- 婚姻 → 財星/官殺
- 出行 → 食傷/財星
- 學習 → 印星/食傷

【M8 命盤存儲】

資料庫結構：
- users: 用戶基本資訊
- charts: 命盤完整資料
- queries: 查詢記錄

操作模式：
- save_result() → 保存命盤
- search_users() → 搜索用戶
- get_chart() → 獲取命盤

【M9 Web界面】

API 端點：
- /api/bazi     → 八字
- /api/full     → 完整命盤
- /api/field    → 場態
- /api/liunian  → 流年
- /api/hepan    → 合盤
- /api/zeri     → 擇日
- /api/now      → 當下
- /api/stats    → 統計
- /api/health   → 健康

【織明語錄】
- 「擇日即擇場」
- 「存儲即場態凝固」
- 「Web即人機橋樑」
"""
