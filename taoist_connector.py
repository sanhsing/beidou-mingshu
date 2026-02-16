#!/usr/bin/env python3
"""
taoist_connector.py - 道家知識庫連接器
========================================
【流祇連結】連接 taoist_v3.db 與 mvp 計算引擎

功能：
1. 天干地支數據讀取
2. 易經卦象查詢
3. 道家原則應用
4. 場論翻譯整合

版本：1.0.0
"""

import sqlite3
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache


# ============================================================
# 資料庫連接
# ============================================================

class TaoistDB:
    """道家知識庫連接器"""
    
    def __init__(self, db_path: str = None):
        """
        初始化連接
        
        db_path: taoist_v3.db 路徑
        """
        if db_path is None:
            # 嘗試多個可能路徑
            possible_paths = [
                '/mnt/user-data/uploads/taoist_v3.db',
                './taoist_v3.db',
                '../taoist_v3.db',
                os.path.join(os.path.dirname(__file__), 'taoist_v3.db')
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    db_path = p
                    break
        
        if db_path is None or not os.path.exists(db_path):
            raise FileNotFoundError("找不到 taoist_v3.db")
        
        self.db_path = db_path
        self._conn = None
    
    @property
    def conn(self) -> sqlite3.Connection:
        """取得連接（懶載入）"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def close(self):
        """關閉連接"""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def query(self, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """執行查詢"""
        cursor = self.conn.execute(sql, params)
        return cursor.fetchall()
    
    def query_one(self, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """查詢單筆"""
        cursor = self.conn.execute(sql, params)
        return cursor.fetchone()


# ============================================================
# 天干地支
# ============================================================

@dataclass
class TianGan:
    """天干"""
    gan: str
    seq: int
    wuxing: str
    yinyang: str
    description: str


@dataclass
class DiZhi:
    """地支"""
    zhi: str
    seq: int
    wuxing: str
    yinyang: str
    canggan: str
    description: str


class GanZhiProvider:
    """天干地支數據提供者"""
    
    def __init__(self, db: TaoistDB):
        self.db = db
        self._tiangan_cache = None
        self._dizhi_cache = None
    
    @property
    def tiangan(self) -> Dict[str, TianGan]:
        """取得所有天干"""
        if self._tiangan_cache is None:
            rows = self.db.query("SELECT * FROM bazi_tiangan ORDER BY seq")
            self._tiangan_cache = {
                row['gan']: TianGan(
                    gan=row['gan'],
                    seq=row['seq'],
                    wuxing=row['wuxing'],
                    yinyang=row['yinyang'],
                    description=row['description']
                )
                for row in rows
            }
        return self._tiangan_cache
    
    @property
    def dizhi(self) -> Dict[str, DiZhi]:
        """取得所有地支"""
        if self._dizhi_cache is None:
            rows = self.db.query("SELECT * FROM bazi_dizhi ORDER BY seq")
            self._dizhi_cache = {
                row['zhi']: DiZhi(
                    zhi=row['zhi'],
                    seq=row['seq'],
                    wuxing=row['wuxing'],
                    yinyang=row['yinyang'],
                    canggan=row['canggan'],
                    description=row['description']
                )
                for row in rows
            }
        return self._dizhi_cache
    
    def get_gan(self, gan: str) -> Optional[TianGan]:
        """取得特定天干"""
        return self.tiangan.get(gan)
    
    def get_zhi(self, zhi: str) -> Optional[DiZhi]:
        """取得特定地支"""
        return self.dizhi.get(zhi)
    
    def get_gan_wuxing(self, gan: str) -> str:
        """取得天干五行"""
        g = self.get_gan(gan)
        return g.wuxing if g else ''
    
    def get_zhi_wuxing(self, zhi: str) -> str:
        """取得地支五行"""
        z = self.get_zhi(zhi)
        return z.wuxing if z else ''
    
    def get_canggan(self, zhi: str) -> List[str]:
        """取得地支藏干"""
        z = self.get_zhi(zhi)
        if z and z.canggan:
            return list(z.canggan)
        return []


# ============================================================
# 易經卦象
# ============================================================

@dataclass
class YijingGua:
    """易經卦象"""
    gua_num: int
    name: str
    full_name: str
    symbol: str
    upper_gua: str
    lower_gua: str
    bit6: int
    guaci: str
    baihua: str
    field_theory: str
    daxiang: str
    keyword: str
    action: str
    warning: str


class YijingProvider:
    """易經數據提供者"""
    
    def __init__(self, db: TaoistDB):
        self.db = db
        self._gua_cache = {}
    
    def get_gua(self, gua_num: int) -> Optional[YijingGua]:
        """取得卦象"""
        if gua_num not in self._gua_cache:
            row = self.db.query_one(
                "SELECT * FROM yijing_gua WHERE gua_num = ?", 
                (gua_num,)
            )
            if row:
                self._gua_cache[gua_num] = YijingGua(
                    gua_num=row['gua_num'],
                    name=row['name'],
                    full_name=row['full_name'] or '',
                    symbol=row['symbol'] or '',
                    upper_gua=row['upper_gua'] or '',
                    lower_gua=row['lower_gua'] or '',
                    bit6=row['bit6'] or 0,
                    guaci=row['guaci'] or '',
                    baihua=row['baihua'] or '',
                    field_theory=row['field_theory'] or '',
                    daxiang=row['daxiang'] or '',
                    keyword=row['keyword'] or '',
                    action=row['action'] or '',
                    warning=row['warning'] or ''
                )
        return self._gua_cache.get(gua_num)
    
    def get_gua_by_name(self, name: str) -> Optional[YijingGua]:
        """依名稱取得卦象"""
        row = self.db.query_one(
            "SELECT * FROM yijing_gua WHERE name = ?", 
            (name,)
        )
        if row:
            return self.get_gua(row['gua_num'])
        return None
    
    def get_all_gua(self) -> List[YijingGua]:
        """取得所有卦象"""
        rows = self.db.query("SELECT gua_num FROM yijing_gua ORDER BY gua_num")
        return [self.get_gua(row['gua_num']) for row in rows]
    
    def get_yao(self, gua_num: int, yao_pos: int) -> Optional[Dict]:
        """取得爻辭"""
        row = self.db.query_one(
            "SELECT * FROM yijing_yao WHERE gua_num = ? AND yao_pos = ?",
            (gua_num, yao_pos)
        )
        if row:
            return dict(row)
        return None


# ============================================================
# 道家原則
# ============================================================

@dataclass
class DaoPrinciple:
    """道家原則"""
    code: str
    name: str
    description: str
    source: str


class DaoProvider:
    """道家原則提供者"""
    
    def __init__(self, db: TaoistDB):
        self.db = db
    
    def get_principles(self) -> List[DaoPrinciple]:
        """取得所有道家原則"""
        rows = self.db.query("SELECT * FROM dao_principles")
        return [
            DaoPrinciple(
                code=row['code'],
                name=row['name'],
                description=row['description'] or '',
                source=row['source'] or ''
            )
            for row in rows
        ]
    
    def get_framework(self) -> List[Dict]:
        """取得道的框架"""
        rows = self.db.query("SELECT * FROM dao_framework")
        return [dict(row) for row in rows]
    
    def get_layers(self) -> List[Dict]:
        """取得六層結構"""
        rows = self.db.query("SELECT * FROM dao_layers ORDER BY layer_level")
        return [dict(row) for row in rows]
    
    def get_stages(self) -> List[Dict]:
        """取得四階段"""
        rows = self.db.query("SELECT * FROM dao_stages ORDER BY stage_order")
        return [dict(row) for row in rows]
    
    def get_field_theory(self) -> List[Dict]:
        """取得場論核心"""
        rows = self.db.query("SELECT * FROM field_theory_core")
        return [dict(row) for row in rows]
    
    def get_xinfa(self) -> List[Dict]:
        """取得心法系統"""
        rows = self.db.query("SELECT * FROM xinfa_core")
        return [dict(row) for row in rows]


# ============================================================
# 道德經
# ============================================================

class DaodejingProvider:
    """道德經提供者"""
    
    def __init__(self, db: TaoistDB):
        self.db = db
    
    def get_chapter(self, chapter: int) -> Optional[Dict]:
        """取得章節"""
        row = self.db.query_one(
            "SELECT * FROM daodejing_chapters WHERE chapter = ?",
            (chapter,)
        )
        return dict(row) if row else None
    
    def get_essence(self, chapter: int) -> Optional[Dict]:
        """取得精華"""
        row = self.db.query_one(
            "SELECT * FROM daodejing_essence WHERE chapter = ?",
            (chapter,)
        )
        return dict(row) if row else None
    
    def get_all_chapters(self) -> List[Dict]:
        """取得所有章節"""
        rows = self.db.query("SELECT * FROM daodejing_chapters ORDER BY chapter")
        return [dict(row) for row in rows]


# ============================================================
# 統一連接器
# ============================================================

class TaoistConnector:
    """
    道家知識庫統一連接器
    
    整合所有數據提供者
    """
    
    _instance = None
    
    def __new__(cls, db_path: str = None):
        """單例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = None):
        if self._initialized:
            return
        
        self.db = TaoistDB(db_path)
        self.ganzhi = GanZhiProvider(self.db)
        self.yijing = YijingProvider(self.db)
        self.dao = DaoProvider(self.db)
        self.daodejing = DaodejingProvider(self.db)
        
        self._initialized = True
    
    def close(self):
        """關閉連接"""
        self.db.close()
    
    # === 便捷方法 ===
    
    def get_tiangan_list(self) -> List[str]:
        """取得天干列表"""
        return list(self.ganzhi.tiangan.keys())
    
    def get_dizhi_list(self) -> List[str]:
        """取得地支列表"""
        return list(self.ganzhi.dizhi.keys())
    
    def get_wuxing(self, ganzhi: str) -> str:
        """取得干支的五行"""
        if len(ganzhi) == 1:
            g = self.ganzhi.get_gan(ganzhi)
            if g:
                return g.wuxing
            z = self.ganzhi.get_zhi(ganzhi)
            if z:
                return z.wuxing
        return ''
    
    def translate_gua(self, gua_num: int) -> Dict:
        """翻譯卦象（場論）"""
        gua = self.yijing.get_gua(gua_num)
        if not gua:
            return {}
        
        return {
            'gua_num': gua.gua_num,
            'name': gua.name,
            'symbol': gua.symbol,
            'keyword': gua.keyword,
            'field_theory': gua.field_theory,
            'action': gua.action,
            'warning': gua.warning
        }
    
    def get_dao_principle(self, code: str) -> Optional[DaoPrinciple]:
        """取得特定道家原則"""
        for p in self.dao.get_principles():
            if p.code == code:
                return p
        return None
    
    def summary(self) -> Dict:
        """取得資料庫摘要"""
        return {
            'tiangan_count': len(self.ganzhi.tiangan),
            'dizhi_count': len(self.ganzhi.dizhi),
            'gua_count': len(self.yijing.get_all_gua()),
            'principles_count': len(self.dao.get_principles()),
            'chapters_count': len(self.daodejing.get_all_chapters()),
            'db_path': self.db.db_path
        }


# ============================================================
# 快捷函數
# ============================================================

_connector = None

def get_connector(db_path: str = None) -> TaoistConnector:
    """取得連接器實例"""
    global _connector
    if _connector is None:
        _connector = TaoistConnector(db_path)
    return _connector


def get_tiangan(gan: str) -> Optional[TianGan]:
    """取得天干"""
    return get_connector().ganzhi.get_gan(gan)


def get_dizhi(zhi: str) -> Optional[DiZhi]:
    """取得地支"""
    return get_connector().ganzhi.get_zhi(zhi)


def get_gua(gua_num: int) -> Optional[YijingGua]:
    """取得卦象"""
    return get_connector().yijing.get_gua(gua_num)


def get_dao_principles() -> List[DaoPrinciple]:
    """取得道家原則"""
    return get_connector().dao.get_principles()


# ============================================================
# 測試
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("TaoistConnector 測試")
    print("=" * 60)
    
    try:
        conn = get_connector()
        
        print("\n【資料庫摘要】")
        summary = conn.summary()
        for k, v in summary.items():
            print(f"  {k}: {v}")
        
        print("\n【天干樣本】")
        for gan in ['甲', '乙', '丙']:
            g = conn.ganzhi.get_gan(gan)
            if g:
                print(f"  {g.gan}: {g.wuxing} {g.yinyang} - {g.description}")
        
        print("\n【地支樣本】")
        for zhi in ['子', '丑', '寅']:
            z = conn.ganzhi.get_zhi(zhi)
            if z:
                print(f"  {z.zhi}: {z.wuxing} {z.yinyang} 藏干:{z.canggan}")
        
        print("\n【卦象樣本】")
        for num in [1, 2, 11]:
            gua = conn.yijing.get_gua(num)
            if gua:
                print(f"  {gua.gua_num}. {gua.name} {gua.symbol} - {gua.keyword}")
        
        print("\n【道家原則】")
        for p in conn.dao.get_principles()[:3]:
            print(f"  {p.code}: {p.name}")
        
        print("\n✓ 測試完成")
        
    except Exception as e:
        print(f"✗ 錯誤: {e}")
