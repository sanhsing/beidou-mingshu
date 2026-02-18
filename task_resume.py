"""
中斷續作機制
task_resume.py | @織明 | 2026-02-17
XTF8 | XTFS | @11星 | PYLIB First

功能：
- 讀取 TASK_CHAIN.json 狀態
- 識別未完成任務
- 生成續作清單
- 支援部分恢復
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

TASK_CHAIN_PATH = Path(__file__).parent / "TASK_CHAIN.json"

class TaskResume:
    """任務續作管理"""
    
    def __init__(self):
        self.chain = self._load_chain()
    
    def _load_chain(self) -> Dict[str, Any]:
        """載入任務鏈"""
        if TASK_CHAIN_PATH.exists():
            return json.load(open(TASK_CHAIN_PATH))
        return {"tasks": []}
    
    def _save_chain(self):
        """保存任務鏈"""
        json.dump(self.chain, open(TASK_CHAIN_PATH, 'w'), indent=2, ensure_ascii=False)
    
    def get_status(self) -> Dict[str, Any]:
        """獲取當前狀態"""
        tasks = self.chain.get('tasks', [])
        
        done = [t for t in tasks if t['status'] == 'done']
        pending = [t for t in tasks if t['status'] == 'pending']
        waiting = [t for t in tasks if t['status'] == 'wait']
        
        by_domain = {}
        for t in tasks:
            domain = t['domain']
            if domain not in by_domain:
                by_domain[domain] = {'done': 0, 'pending': 0, 'total': 0}
            by_domain[domain]['total'] += 1
            if t['status'] == 'done':
                by_domain[domain]['done'] += 1
            else:
                by_domain[domain]['pending'] += 1
        
        return {
            'total': len(tasks),
            'done': len(done),
            'pending': len(pending) + len(waiting),
            'completion': round(len(done) / len(tasks) * 100, 1) if tasks else 0,
            'by_domain': by_domain,
            'next_tasks': self.get_next_tasks()
        }
    
    def get_next_tasks(self) -> List[Dict]:
        """獲取下一批可執行任務 (依賴已滿足)"""
        tasks = self.chain.get('tasks', [])
        done_ids = {t['id'] for t in tasks if t['status'] == 'done'}
        
        next_tasks = []
        for t in tasks:
            if t['status'] != 'done':
                deps = t.get('deps', [])
                # 檢查依賴是否都已完成
                deps_met = all(d in done_ids for d in deps)
                if deps_met:
                    next_tasks.append(t)
        
        return next_tasks
    
    def mark_done(self, task_id: str) -> bool:
        """標記任務完成"""
        for t in self.chain.get('tasks', []):
            if t['id'] == task_id:
                t['status'] = 'done'
                t['completed_at'] = datetime.now().isoformat()
                self._save_chain()
                return True
        return False
    
    def mark_pending(self, task_id: str) -> bool:
        """標記任務待處理"""
        for t in self.chain.get('tasks', []):
            if t['id'] == task_id:
                t['status'] = 'pending'
                self._save_chain()
                return True
        return False
    
    def get_task(self, task_id: str) -> Dict:
        """獲取單個任務"""
        for t in self.chain.get('tasks', []):
            if t['id'] == task_id:
                return t
        return {}
    
    def get_tasks_by_domain(self, domain: str) -> List[Dict]:
        """按領域獲取任務"""
        return [t for t in self.chain.get('tasks', []) if t['domain'] == domain]
    
    def get_tasks_by_star(self, star: str) -> List[Dict]:
        """按星官獲取任務"""
        return [t for t in self.chain.get('tasks', []) if t.get('star') == star]
    
    def print_status(self):
        """打印狀態報告"""
        status = self.get_status()
        
        print("=" * 60)
        print("  XTF Task Chain - 中斷續作狀態")
        print("=" * 60)
        print(f"\n總進度: {status['done']}/{status['total']} ({status['completion']}%)")
        print("\n【各領域進度】")
        
        domain_names = {
            'L': '法務文件', 'F': '前端頁面', 'A': '後端API',
            'P': '商業閉環', 'D': '部署工具', 'X': '整合', 'T': '外部任務'
        }
        
        for d, s in status['by_domain'].items():
            name = domain_names.get(d, d)
            pct = round(s['done'] / s['total'] * 100) if s['total'] else 0
            bar = '█' * (pct // 10) + '░' * (10 - pct // 10)
            icon = '✅' if pct == 100 else '⏳'
            print(f"  {icon} {name:10} [{bar}] {s['done']}/{s['total']}")
        
        print("\n【可執行任務】")
        for t in status['next_tasks'][:5]:
            print(f"  → {t['id']} {t['name']} ({t.get('star', '')})")
        
        if len(status['next_tasks']) > 5:
            print(f"  ... 還有 {len(status['next_tasks']) - 5} 個任務")


def resume() -> Dict[str, Any]:
    """快捷函數：獲取續作狀態"""
    tr = TaskResume()
    tr.print_status()
    return tr.get_status()


def mark(task_id: str, status: str = 'done') -> bool:
    """快捷函數：標記任務"""
    tr = TaskResume()
    if status == 'done':
        return tr.mark_done(task_id)
    else:
        return tr.mark_pending(task_id)


if __name__ == "__main__":
    import sys
    
    tr = TaskResume()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == 'status':
            tr.print_status()
        
        elif cmd == 'next':
            print("【可執行任務】")
            for t in tr.get_next_tasks():
                print(f"  {t['id']} {t['name']:15} │ {t['file'] or '(外部)'} │ {t.get('star', '')}")
        
        elif cmd == 'done' and len(sys.argv) > 2:
            task_id = sys.argv[2]
            if tr.mark_done(task_id):
                print(f"✅ {task_id} 已標記完成")
            else:
                print(f"❌ 找不到任務 {task_id}")
        
        elif cmd == 'domain' and len(sys.argv) > 2:
            domain = sys.argv[2].upper()
            tasks = tr.get_tasks_by_domain(domain)
            print(f"【{domain} 領域任務】")
            for t in tasks:
                icon = '✅' if t['status'] == 'done' else '⏳'
                print(f"  {icon} {t['id']} {t['name']}")
        
        else:
            print("用法:")
            print("  python task_resume.py status     # 查看狀態")
            print("  python task_resume.py next       # 查看可執行任務")
            print("  python task_resume.py done T01   # 標記任務完成")
            print("  python task_resume.py domain L   # 查看領域任務")
    else:
        tr.print_status()
