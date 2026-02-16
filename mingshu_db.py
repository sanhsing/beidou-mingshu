"""
命數資料庫 CRUD API mingshu_db.py v1.1
=====================================
XTF任務：消-D2 | 執行星：流祇（連結）
確定度：★★★★★（API 操作確定）

核心本質：API = 儲存 + 查詢 + 更新
表名前綴：ms_（與 mingshu_schema.py 一致）
"""

import sqlite3
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from mingshu_schema import init_mingshu_db, get_schema_info


def get_db_path() -> str:
    """取得資料庫路徑"""
    import os
    paths = ["./mingshu.db", "/home/claude/db/mingshu.db"]
    for p in paths:
        d = os.path.dirname(p) or "."
        if os.path.exists(d):
            return p
    return "./mingshu.db"


# ============================================================
# 資料類別
# ============================================================

@dataclass
class UserData:
    """用戶資料"""
    name: str = ""
    gender: str = "男"
    birth_year: int = 2000
    birth_month: int = 1
    birth_day: int = 1
    birth_hour: int = 12
    is_lunar: bool = False
    leap_month: bool = False


@dataclass
class BaziData:
    """八字資料"""
    year_gan: str = ""
    year_zhi: str = ""
    month_gan: str = ""
    month_zhi: str = ""
    day_gan: str = ""
    day_zhi: str = ""
    hour_gan: str = ""
    hour_zhi: str = ""
    day_master: str = ""
    day_master_wx: str = ""
    strength_score: int = 0
    strength_level: str = ""
    yongshen: str = ""
    xishen: str = ""
    jishen: str = ""
    geju_name: str = ""
    geju_field: str = ""
    wx_count: Dict = None


@dataclass
class ZiweiData:
    """紫微資料"""
    ju_shu: str = ""
    ming_gong: str = ""
    ming_gong_idx: int = 0
    shen_gong: str = ""
    shen_gong_idx: int = 0
    ming_stars: List[str] = None
    shen_stars: List[str] = None
    sihua: Dict = None
    gongs_data: str = ""


# ============================================================
# 資料庫操作類別
# ============================================================

class MingshuDB:
    """命數資料庫操作類別"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or get_db_path()
        self._ensure_db()
    
    def _ensure_db(self):
        """確保資料庫存在"""
        conn = init_mingshu_db(self.db_path)
        conn.close()
    
    def _get_conn(self) -> sqlite3.Connection:
        """取得連接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ========== 用戶 CRUD ==========
    
    def create_user(self, user: UserData) -> int:
        """新增用戶"""
        conn = self._get_conn()
        try:
            user_uuid = str(uuid.uuid4())
            cursor = conn.execute("""
                INSERT INTO ms_users 
                (uuid, name, gender, birth_year, birth_month, birth_day, birth_hour, is_lunar, leap_month)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_uuid, user.name, user.gender, user.birth_year, user.birth_month,
                user.birth_day, user.birth_hour, int(user.is_lunar), int(user.leap_month)
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """查詢用戶"""
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT * FROM ms_users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def find_user(self, name: str = None, birth_year: int = None) -> List[Dict]:
        """搜尋用戶"""
        conn = self._get_conn()
        try:
            conditions = []
            params = []
            if name:
                conditions.append("name LIKE ?")
                params.append(f"%{name}%")
            if birth_year:
                conditions.append("birth_year = ?")
                params.append(birth_year)
            
            where = " AND ".join(conditions) if conditions else "1=1"
            cursor = conn.execute(f"SELECT * FROM ms_users WHERE {where}", params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def delete_user(self, user_id: int) -> bool:
        """刪除用戶（連帶刪除關聯資料）"""
        conn = self._get_conn()
        try:
            tables = ['ms_bazi', 'ms_ziwei', 'ms_dayun', 'ms_daxian', 'ms_liunian', 'ms_reports', 'ms_shensha']
            for t in tables:
                try:
                    conn.execute(f"DELETE FROM {t} WHERE user_id = ?", (user_id,))
                except:
                    pass
            conn.execute("DELETE FROM ms_users WHERE id = ?", (user_id,))
            conn.commit()
            return True
        finally:
            conn.close()
    
    # ========== 八字 CRUD ==========
    
    def save_bazi(self, user_id: int, bazi: BaziData) -> int:
        """儲存八字命盤"""
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT id FROM ms_bazi WHERE user_id = ?", (user_id,))
            existing = cursor.fetchone()
            
            wx = bazi.wx_count or {}
            
            if existing:
                conn.execute("""
                    UPDATE ms_bazi SET
                        year_gan=?, year_zhi=?, month_gan=?, month_zhi=?,
                        day_gan=?, day_zhi=?, hour_gan=?, hour_zhi=?,
                        day_master=?, day_master_wx=?, strength_score=?, strength_level=?,
                        yongshen=?, xishen=?, jishen=?, geju_name=?, geju_field=?,
                        wx_mu=?, wx_huo=?, wx_tu=?, wx_jin=?, wx_shui=?
                    WHERE user_id = ?
                """, (
                    bazi.year_gan, bazi.year_zhi, bazi.month_gan, bazi.month_zhi,
                    bazi.day_gan, bazi.day_zhi, bazi.hour_gan, bazi.hour_zhi,
                    bazi.day_master, bazi.day_master_wx, bazi.strength_score, bazi.strength_level,
                    bazi.yongshen, bazi.xishen, bazi.jishen, bazi.geju_name, bazi.geju_field,
                    wx.get("木", 0), wx.get("火", 0), wx.get("土", 0), wx.get("金", 0), wx.get("水", 0),
                    user_id
                ))
                conn.commit()
                return existing[0]
            else:
                cursor = conn.execute("""
                    INSERT INTO ms_bazi 
                    (user_id, year_gan, year_zhi, month_gan, month_zhi,
                     day_gan, day_zhi, hour_gan, hour_zhi,
                     day_master, day_master_wx, strength_score, strength_level,
                     yongshen, xishen, jishen, geju_name, geju_field,
                     wx_mu, wx_huo, wx_tu, wx_jin, wx_shui)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, bazi.year_gan, bazi.year_zhi, bazi.month_gan, bazi.month_zhi,
                    bazi.day_gan, bazi.day_zhi, bazi.hour_gan, bazi.hour_zhi,
                    bazi.day_master, bazi.day_master_wx, bazi.strength_score, bazi.strength_level,
                    bazi.yongshen, bazi.xishen, bazi.jishen, bazi.geju_name, bazi.geju_field,
                    wx.get("木", 0), wx.get("火", 0), wx.get("土", 0), wx.get("金", 0), wx.get("水", 0)
                ))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()
    
    def get_bazi(self, user_id: int) -> Optional[Dict]:
        """查詢八字命盤"""
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT * FROM ms_bazi WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['wx_count'] = {
                    "木": result.get('wx_mu', 0),
                    "火": result.get('wx_huo', 0),
                    "土": result.get('wx_tu', 0),
                    "金": result.get('wx_jin', 0),
                    "水": result.get('wx_shui', 0),
                }
                return result
            return None
        finally:
            conn.close()
    
    # ========== 紫微 CRUD ==========
    
    def save_ziwei(self, user_id: int, ziwei: ZiweiData) -> int:
        """儲存紫微命盤"""
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT id FROM ms_ziwei WHERE user_id = ?", (user_id,))
            existing = cursor.fetchone()
            
            sihua = ziwei.sihua or {}
            ming_stars_str = ",".join(ziwei.ming_stars or [])
            shen_stars_str = ",".join(ziwei.shen_stars or [])
            
            if existing:
                conn.execute("""
                    UPDATE ms_ziwei SET
                        ju_shu=?, ming_gong=?, ming_gong_idx=?, shen_gong=?, shen_gong_idx=?,
                        ming_stars=?, shen_stars=?,
                        sihua_lu=?, sihua_quan=?, sihua_ke=?, sihua_ji=?, gongs_data=?
                    WHERE user_id = ?
                """, (
                    ziwei.ju_shu, ziwei.ming_gong, ziwei.ming_gong_idx, ziwei.shen_gong, ziwei.shen_gong_idx,
                    ming_stars_str, shen_stars_str,
                    sihua.get("祿", ""), sihua.get("權", ""), sihua.get("科", ""), sihua.get("忌", ""),
                    ziwei.gongs_data, user_id
                ))
                conn.commit()
                return existing[0]
            else:
                cursor = conn.execute("""
                    INSERT INTO ms_ziwei 
                    (user_id, ju_shu, ming_gong, ming_gong_idx, shen_gong, shen_gong_idx,
                     ming_stars, shen_stars, sihua_lu, sihua_quan, sihua_ke, sihua_ji, gongs_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, ziwei.ju_shu, ziwei.ming_gong, ziwei.ming_gong_idx, ziwei.shen_gong, ziwei.shen_gong_idx,
                    ming_stars_str, shen_stars_str,
                    sihua.get("祿", ""), sihua.get("權", ""), sihua.get("科", ""), sihua.get("忌", ""),
                    ziwei.gongs_data
                ))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()
    
    def get_ziwei(self, user_id: int) -> Optional[Dict]:
        """查詢紫微命盤"""
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT * FROM ms_ziwei WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['ming_stars'] = result.get('ming_stars', '').split(',') if result.get('ming_stars') else []
                result['shen_stars'] = result.get('shen_stars', '').split(',') if result.get('shen_stars') else []
                result['sihua'] = {
                    "祿": result.get('sihua_lu', ''),
                    "權": result.get('sihua_quan', ''),
                    "科": result.get('sihua_ke', ''),
                    "忌": result.get('sihua_ji', ''),
                }
                return result
            return None
        finally:
            conn.close()
    
    # ========== 大運/大限 CRUD ==========
    
    def save_dayun(self, user_id: int, dayun_list: List[Dict]) -> int:
        """儲存八字大運"""
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM ms_dayun WHERE user_id = ?", (user_id,))
            for d in dayun_list:
                conn.execute("""
                    INSERT INTO ms_dayun (user_id, order_num, ganzhi, start_age, end_age, start_year, end_year, analysis)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, d.get('order'), d.get('ganzhi'),
                    d.get('start_age'), d.get('end_age'), d.get('start_year'), d.get('end_year'),
                    json.dumps(d, ensure_ascii=False)
                ))
            conn.commit()
            return len(dayun_list)
        finally:
            conn.close()
    
    def get_dayun(self, user_id: int) -> List[Dict]:
        """查詢八字大運"""
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT * FROM ms_dayun WHERE user_id = ? ORDER BY order_num", (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_daxian(self, user_id: int, daxian_list: List[Dict]) -> int:
        """儲存紫微大限"""
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM ms_daxian WHERE user_id = ?", (user_id,))
            for d in daxian_list:
                conn.execute("""
                    INSERT INTO ms_daxian (user_id, order_num, gong_name, gong_zhi, start_age, end_age, start_year, end_year, analysis)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, d.get('order'), d.get('gong_name'), d.get('gong_zhi'),
                    d.get('start_age'), d.get('end_age'), d.get('start_year'), d.get('end_year'),
                    json.dumps(d, ensure_ascii=False)
                ))
            conn.commit()
            return len(daxian_list)
        finally:
            conn.close()
    
    def get_daxian(self, user_id: int) -> List[Dict]:
        """查詢紫微大限"""
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT * FROM ms_daxian WHERE user_id = ? ORDER BY order_num", (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # ========== 報告 CRUD ==========
    
    def save_report(self, user_id: int, report_type: str, report_text: str, report_json: str = "") -> int:
        """儲存報告"""
        conn = self._get_conn()
        try:
            cursor = conn.execute("""
                INSERT INTO ms_reports (user_id, report_type, report_text, report_json)
                VALUES (?, ?, ?, ?)
            """, (user_id, report_type, report_text, report_json))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_latest_report(self, user_id: int, report_type: str = 'full') -> Optional[Dict]:
        """取得最新報告"""
        conn = self._get_conn()
        try:
            cursor = conn.execute("""
                SELECT * FROM ms_reports WHERE user_id = ? AND report_type = ?
                ORDER BY created_at DESC LIMIT 1
            """, (user_id, report_type))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    # ========== 統計 ==========
    
    def get_stats(self) -> Dict:
        """取得統計資料"""
        conn = self._get_conn()
        try:
            stats = {}
            tables = ['ms_users', 'ms_bazi', 'ms_ziwei', 'ms_dayun', 'ms_daxian', 'ms_liunian', 'ms_reports']
            for table in tables:
                try:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cursor.fetchone()[0]
                except:
                    stats[table] = 0
            return stats
        finally:
            conn.close()


# ============================================================
# 便捷函數
# ============================================================

_db: MingshuDB = None

def get_db(db_path: str = None) -> MingshuDB:
    """取得資料庫實例"""
    global _db
    if _db is None or db_path:
        _db = MingshuDB(db_path)
    return _db


if __name__ == "__main__":
    print("測試 MingshuDB...")
    
    db = MingshuDB("./test_mingshu.db")
    
    # 測試新增用戶
    user = UserData(name="北斗測試", gender="男", birth_year=1973, birth_month=12, birth_day=30, birth_hour=17)
    user_id = db.create_user(user)
    print(f"✅ 新增用戶 ID: {user_id}")
    
    # 測試儲存八字
    bazi = BaziData(
        year_gan="癸", year_zhi="丑",
        month_gan="甲", month_zhi="子",
        day_gan="庚", day_zhi="子",
        hour_gan="乙", hour_zhi="酉",
        day_master="庚", day_master_wx="金",
        strength_level="極弱", geju_name="傷官格",
        wx_count={"木": 2, "火": 0, "土": 2, "金": 2, "水": 4}
    )
    db.save_bazi(user_id, bazi)
    print("✅ 八字已儲存")
    
    # 測試查詢
    bazi_data = db.get_bazi(user_id)
    print(f"✅ 查詢八字：{bazi_data['day_master']}日主，{bazi_data['geju_name']}")
    
    # 測試統計
    stats = db.get_stats()
    print(f"✅ 統計: {stats}")
    
    # 清理
    import os
    os.remove("./test_mingshu.db")
    print("\n✅ MingshuDB 測試完成")
