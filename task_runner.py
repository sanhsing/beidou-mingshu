"""
XTF Task Runner - 中斷續作支援
task_runner.py | @織明 | 2026-02-17
PYLIB: logger, config

功能：
- 載入任務鏈
- 執行原子任務
- 中斷點保存/恢復
- 並行/串行調度
"""
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field, asdict

# === 配置 ===
PROJECT_ROOT = Path(__file__).parent
CHECKPOINT_FILE = PROJECT_ROOT / "task_checkpoint.json"
TELEGRAM_BOT = '8080151081:AAEV7amkwA7l2VEKteah7r2kyMEcWhI8NUc'
TELEGRAM_CHAT = '5965951659'


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class Task:
    """原子任務"""
    id: str
    name: str
    module: str
    depends_on: List[str] = field(default_factory=list)
    parallel: bool = True
    assignee: str = ""
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error: Optional[str] = None


@dataclass
class Checkpoint:
    """中斷點"""
    version: str = "2.0"
    current_phase: int = 1
    current_batch: str = ""
    tasks: Dict[str, str] = field(default_factory=dict)
    last_updated: str = ""
    
    def save(self, path: Path = CHECKPOINT_FILE):
        """保存中斷點"""
        self.last_updated = datetime.now().isoformat()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: Path = CHECKPOINT_FILE) -> 'Checkpoint':
        """載入中斷點"""
        if not path.exists():
            return cls()
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return cls(**data)


# === 任務定義 ===
TASK_CHAIN = {
    # M1: 法務文件
    "L1.1": Task("L1.1", "建立 legal/children.md", "M1", [], True, "@澄書"),
    "L1.2": Task("L1.2", "添加兒童保護路由", "M1", ["L1.1"], False, "@星殼"),
    "L1.3": Task("L1.3", "更新 privacy.md 兒童章節", "M1", ["L1.1"], True, "@澄書"),
    "L1.4": Task("L1.4", "法務頁面 footer 統一", "M1", [], True, "@璃語"),
    "L1.5": Task("L1.5", "添加「同意」確認機制", "M1", ["L1.4"], False, "@星殼"),
    "L1.6": Task("L1.6", "法務頁面 SEO meta", "M1", [], True, "@璃語"),
    "L1.7": Task("L1.7", "法務內容繁簡轉換", "M1", [], True, "@澄書"),
    "L1.8": Task("L1.8", "法務文件版本號管理", "M1", [], True, "@理樞"),
    
    # M2: 前端頁面 (缺口補完)
    "F2.1": Task("F2.1", "建立 about_page.py 框架", "M2", [], True, "@璃語"),
    "F2.2": Task("F2.2", "關於頁-品牌故事區塊", "M2", ["F2.1"], False, "@璃語"),
    "F2.3": Task("F2.3", "關於頁-團隊介紹區塊", "M2", ["F2.1"], True, "@澄書"),
    "F2.4": Task("F2.4", "關於頁-聯繫方式區塊", "M2", ["F2.1"], True, "@璃語"),
    "F2.5": Task("F2.5", "建立 error_pages.py", "M2", [], True, "@星殼"),
    "F2.6": Task("F2.6", "404 頁面設計", "M2", ["F2.5"], False, "@璃語"),
    "F2.7": Task("F2.7", "500 頁面設計", "M2", ["F2.5"], True, "@璃語"),
    "F2.8": Task("F2.8", "建立 settings_page.py", "M2", [], True, "@星殼"),
    "F2.9": Task("F2.9", "設定頁-個人資料區塊", "M2", ["F2.8"], False, "@璃語"),
    "F2.10": Task("F2.10", "設定頁-密碼修改區塊", "M2", ["F2.8"], True, "@星殼"),
    "F2.11": Task("F2.11", "設定頁-通知偏好區塊", "M2", ["F2.8"], True, "@璃語"),
    
    # M2: 前端頁面 (優化)
    "F2.12": Task("F2.12", "landing_page SEO 優化", "M2", [], True, "@璃語"),
    "F2.13": Task("F2.13", "landing_page 社交分享 meta", "M2", [], True, "@璃語"),
    "F2.14": Task("F2.14", "dashboard 圖表整合", "M2", [], True, "@理樞"),
    "F2.15": Task("F2.15", "dashboard 快捷操作優化", "M2", [], True, "@璃語"),
    "F2.16": Task("F2.16", "pricing_page 比較表", "M2", [], True, "@璃語"),
    "F2.17": Task("F2.17", "checkout 進度指示器", "M2", [], True, "@璃語"),
    "F2.18": Task("F2.18", "matching_page 歷史記錄", "M2", [], True, "@星殼"),
    "F2.19": Task("F2.19", "全站 loading 動畫", "M2", [], True, "@璃語"),
    "F2.20": Task("F2.20", "全站 toast 通知組件", "M2", [], True, "@星殼"),
    "F2.21": Task("F2.21", "響應式導航欄優化", "M2", [], True, "@璃語"),
    "F2.22": Task("F2.22", "頁腳統一組件", "M2", [], True, "@璃語"),
    "F2.23": Task("F2.23", "深色模式支援", "M2", ["F2.22"], False, "@璃語"),
    "F2.24": Task("F2.24", "無障礙 (a11y) 優化", "M2", [], True, "@澄書"),
    
    # M3: 後端API
    "A3.1": Task("A3.1", "建立 user_settings_api.py", "M3", [], True, "@星殼"),
    "A3.2": Task("A3.2", "GET /api/user/profile", "M3", ["A3.1"], False, "@星殼"),
    "A3.3": Task("A3.3", "PUT /api/user/profile", "M3", ["A3.1"], True, "@星殼"),
    "A3.4": Task("A3.4", "POST /api/user/password", "M3", ["A3.1"], True, "@星殼"),
    "A3.5": Task("A3.5", "PUT /api/user/notifications", "M3", ["A3.1"], True, "@星殼"),
    "A3.6": Task("A3.6", "建立 admin_stats_api.py", "M3", [], True, "@理樞"),
    "A3.7": Task("A3.7", "GET /api/admin/stats/users", "M3", ["A3.6"], False, "@理樞"),
    "A3.8": Task("A3.8", "GET /api/admin/stats/orders", "M3", ["A3.6"], True, "@理樞"),
    "A3.9": Task("A3.9", "GET /api/admin/stats/revenue", "M3", ["A3.6"], True, "@理樞"),
    "A3.10": Task("A3.10", "auth_jwt refresh token", "M3", [], True, "@星殼"),
    "A3.11": Task("A3.11", "credits_api 分頁支援", "M3", [], True, "@星殼"),
    "A3.12": Task("A3.12", "payment_service 重試機制", "M3", [], True, "@星殼"),
    "A3.13": Task("A3.13", "API 統一錯誤格式", "M3", [], True, "@理樞"),
    "A3.14": Task("A3.14", "API 請求日誌中間件", "M3", [], True, "@理樞"),
    "A3.15": Task("A3.15", "API 限流中間件", "M3", ["A3.14"], False, "@星殼"),
    "A3.16": Task("A3.16", "API 文檔自動生成", "M3", [], True, "@理樞"),
    
    # M4: 商業閉環
    "P4.1": Task("P4.1", "建立 coupon_service.py", "M4", [], True, "@星殼"),
    "P4.2": Task("P4.2", "優惠券 CRUD API", "M4", ["P4.1"], False, "@星殼"),
    "P4.3": Task("P4.3", "優惠券驗證邏輯", "M4", ["P4.1"], True, "@星殼"),
    "P4.4": Task("P4.4", "checkout 整合優惠券", "M4", ["P4.2", "P4.3"], False, "@璃語"),
    "P4.5": Task("P4.5", "建立 invoice_service.py", "M4", [], True, "@星殼"),
    "P4.6": Task("P4.6", "電子發票 API 整合", "M4", ["P4.5"], False, "@星殼"),
    "P4.7": Task("P4.7", "發票查詢頁面", "M4", ["P4.6"], False, "@璃語"),
    "P4.8": Task("P4.8", "payment_flow 異常處理", "M4", [], True, "@星殼"),
    "P4.9": Task("P4.9", "支付超時自動取消", "M4", [], True, "@星殼"),
    "P4.10": Task("P4.10", "會員到期提醒", "M4", [], True, "@流祇"),
    "P4.11": Task("P4.11", "點數過期機制", "M4", [], True, "@星殼"),
    "P4.12": Task("P4.12", "訂單匯出功能", "M4", [], True, "@理樞"),
}

# 批次定義
BATCHES = {
    "1.1": ["L1.1", "F2.1", "F2.5", "F2.8"],
    "1.2": ["A3.1", "A3.6", "P4.1", "P4.5"],
    "1.3": ["L1.2", "F2.2", "A3.2", "P4.2"],
    "1.4": ["F2.6", "A3.7", "P4.6"],
    "2.1": ["F2.3", "F2.4", "F2.9", "F2.10", "F2.11", "A3.3", "A3.4", "A3.5"],
    "2.2": ["F2.7", "P4.3", "P4.4", "A3.8", "A3.9"],
    "2.3": ["L1.3", "L1.4", "L1.5", "L1.6", "L1.7", "L1.8"],
    "2.4": ["P4.7", "F2.12", "F2.13", "F2.14", "F2.15", "F2.16", "F2.17"],
    "2.5": ["A3.10", "A3.11", "A3.12", "A3.13", "A3.14"],
    "3.1": ["F2.18", "F2.19", "F2.20", "F2.21", "F2.22"],
    "3.2": ["F2.23", "F2.24", "A3.15", "A3.16"],
    "3.3": ["P4.8", "P4.9", "P4.10", "P4.11", "P4.12"],
}


class TaskRunner:
    """任務執行器"""
    
    def __init__(self):
        self.checkpoint = Checkpoint.load()
        self.tasks = TASK_CHAIN.copy()
        self._restore_state()
    
    def _restore_state(self):
        """從 checkpoint 恢復狀態"""
        for task_id, status in self.checkpoint.tasks.items():
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus(status)
    
    def _can_run(self, task: Task) -> bool:
        """檢查任務是否可執行"""
        if task.status != TaskStatus.PENDING:
            return False
        
        for dep_id in task.depends_on:
            dep_task = self.tasks.get(dep_id)
            if dep_task and dep_task.status != TaskStatus.DONE:
                return False
        
        return True
    
    def _get_runnable_tasks(self, batch: str = None) -> List[Task]:
        """獲取可執行的任務"""
        runnable = []
        
        if batch:
            task_ids = BATCHES.get(batch, [])
            for tid in task_ids:
                task = self.tasks.get(tid)
                if task and self._can_run(task):
                    runnable.append(task)
        else:
            for task in self.tasks.values():
                if self._can_run(task):
                    runnable.append(task)
        
        return runnable
    
    def _update_checkpoint(self, task: Task):
        """更新 checkpoint"""
        self.checkpoint.tasks[task.id] = task.status.value
        self.checkpoint.save()
    
    def run_task(self, task: Task) -> bool:
        """執行單個任務 (模擬)"""
        print(f"  🔄 執行: {task.id} - {task.name} ({task.assignee})")
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        self._update_checkpoint(task)
        
        # 模擬執行
        time.sleep(0.1)
        
        task.status = TaskStatus.DONE
        task.finished_at = datetime.now().isoformat()
        self._update_checkpoint(task)
        print(f"  ✅ 完成: {task.id}")
        
        return True
    
    def run_batch(self, batch: str):
        """執行一個批次"""
        print(f"\n{'='*60}")
        print(f"  批次 {batch}")
        print(f"{'='*60}")
        
        self.checkpoint.current_batch = batch
        self.checkpoint.save()
        
        tasks = self._get_runnable_tasks(batch)
        
        if not tasks:
            print("  ⚠️ 無可執行任務 (可能有未完成的依賴)")
            return
        
        for task in tasks:
            self.run_task(task)
    
    def run_all(self):
        """執行所有批次"""
        for batch in sorted(BATCHES.keys()):
            self.run_batch(batch)
        
        self.print_summary()
    
    def run_module(self, module: str):
        """執行特定模組的任務"""
        tasks = [t for t in self.tasks.values() 
                 if t.module == module and self._can_run(t)]
        
        print(f"\n{'='*60}")
        print(f"  模組 {module} ({len(tasks)} 個任務)")
        print(f"{'='*60}")
        
        for task in tasks:
            self.run_task(task)
    
    def resume(self):
        """從中斷點續作"""
        print(f"\n{'='*60}")
        print(f"  從中斷點續作")
        print(f"  上次更新: {self.checkpoint.last_updated}")
        print(f"  當前批次: {self.checkpoint.current_batch}")
        print(f"{'='*60}")
        
        # 找到第一個未完成的批次
        for batch in sorted(BATCHES.keys()):
            tasks = BATCHES[batch]
            all_done = all(
                self.tasks[tid].status == TaskStatus.DONE 
                for tid in tasks if tid in self.tasks
            )
            if not all_done:
                self.run_batch(batch)
        
        self.print_summary()
    
    def print_summary(self):
        """打印摘要"""
        done = sum(1 for t in self.tasks.values() if t.status == TaskStatus.DONE)
        total = len(self.tasks)
        
        print(f"\n{'='*60}")
        print(f"  執行摘要")
        print(f"{'='*60}")
        print(f"  完成: {done}/{total} ({done/total*100:.1f}%)")
        
        by_module = {}
        for task in self.tasks.values():
            m = task.module
            if m not in by_module:
                by_module[m] = {'done': 0, 'total': 0}
            by_module[m]['total'] += 1
            if task.status == TaskStatus.DONE:
                by_module[m]['done'] += 1
        
        for m, stats in sorted(by_module.items()):
            print(f"  {m}: {stats['done']}/{stats['total']}")
    
    def get_status(self) -> Dict[str, Any]:
        """獲取當前狀態"""
        done = sum(1 for t in self.tasks.values() if t.status == TaskStatus.DONE)
        total = len(self.tasks)
        
        return {
            'done': done,
            'total': total,
            'percent': done / total * 100,
            'current_batch': self.checkpoint.current_batch,
            'last_updated': self.checkpoint.last_updated
        }


def notify_telegram(message: str) -> bool:
    """發送 Telegram 通知"""
    import urllib.request
    import urllib.parse
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': TELEGRAM_CHAT,
            'text': message,
            'parse_mode': 'Markdown'
        }).encode()
        
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=10)
        return True
    except:
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='XTF Task Runner')
    parser.add_argument('--resume', action='store_true', help='從中斷點續作')
    parser.add_argument('--batch', type=str, help='執行特定批次')
    parser.add_argument('--module', type=str, help='執行特定模組 (M1/M2/M3/M4)')
    parser.add_argument('--status', action='store_true', help='查看狀態')
    parser.add_argument('--reset', action='store_true', help='重置 checkpoint')
    
    args = parser.parse_args()
    
    runner = TaskRunner()
    
    if args.status:
        status = runner.get_status()
        print(f"進度: {status['done']}/{status['total']} ({status['percent']:.1f}%)")
        print(f"當前批次: {status['current_batch']}")
        print(f"上次更新: {status['last_updated']}")
    elif args.reset:
        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()
        print("✅ Checkpoint 已重置")
    elif args.resume:
        runner.resume()
    elif args.batch:
        runner.run_batch(args.batch)
    elif args.module:
        runner.run_module(args.module)
    else:
        runner.run_all()
