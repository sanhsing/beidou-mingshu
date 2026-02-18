"""
備份模組 - C 備份
deploy/backup.py | @星殼 | 2026-02-17
PYLIB: logger, config

功能：
- 打包完整項目
- 差分備份（僅變更文件）
- 生成備份清單
- Telegram 通知
"""
import os
import sys
import json
import tarfile
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# === 配置 ===
PROJECT_ROOT = Path(__file__).parent.parent
BACKUP_DIR = PROJECT_ROOT / "backups"
EXCLUDE_PATTERNS = [
    '__pycache__', '.git', 'node_modules', '*.pyc', '*.db',
    'backups', '.env', 'logs', '*.log', '.DS_Store'
]

class BackupService:
    """備份服務"""
    
    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = project_root
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(exist_ok=True)
        self.manifest = {}
    
    def _should_exclude(self, path: str) -> bool:
        """檢查是否應排除"""
        for pattern in EXCLUDE_PATTERNS:
            if pattern.startswith('*'):
                if path.endswith(pattern[1:]):
                    return True
            elif pattern in path:
                return True
        return False
    
    def _file_hash(self, filepath: Path) -> str:
        """計算文件 MD5"""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def scan_files(self) -> Dict[str, dict]:
        """掃描所有文件"""
        files = {}
        for root, dirs, filenames in os.walk(self.project_root):
            # 排除目錄
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]
            
            for filename in filenames:
                filepath = Path(root) / filename
                relpath = str(filepath.relative_to(self.project_root))
                
                if self._should_exclude(relpath):
                    continue
                
                stat = filepath.stat()
                files[relpath] = {
                    'size': stat.st_size,
                    'mtime': stat.st_mtime,
                    'hash': self._file_hash(filepath) if stat.st_size < 10*1024*1024 else None
                }
        
        return files
    
    def create_full_backup(self, name: str = None) -> Tuple[Path, dict]:
        """創建完整備份"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = name or f"beidou_full_{timestamp}"
        
        archive_path = self.backup_dir / f"{name}.tar.gz"
        manifest_path = self.backup_dir / f"{name}_manifest.json"
        
        print(f"[Backup] 開始完整備份: {name}")
        
        # 掃描文件
        files = self.scan_files()
        print(f"[Backup] 掃描到 {len(files)} 個文件")
        
        # 創建壓縮包
        with tarfile.open(archive_path, "w:gz") as tar:
            for relpath in files:
                filepath = self.project_root / relpath
                tar.add(filepath, arcname=relpath)
        
        # 保存清單
        manifest = {
            'name': name,
            'type': 'full',
            'created': datetime.now().isoformat(),
            'file_count': len(files),
            'archive_size': archive_path.stat().st_size,
            'files': files
        }
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"[Backup] 完成: {archive_path}")
        print(f"[Backup] 大小: {manifest['archive_size'] / 1024 / 1024:.2f} MB")
        
        return archive_path, manifest
    
    def create_diff_backup(self, base_manifest_path: Path, name: str = None) -> Tuple[Path, dict]:
        """創建差分備份"""
        # 載入基準清單
        with open(base_manifest_path, 'r', encoding='utf-8') as f:
            base_manifest = json.load(f)
        
        base_files = base_manifest.get('files', {})
        current_files = self.scan_files()
        
        # 找出變更
        changed = []
        added = []
        deleted = []
        
        for relpath, info in current_files.items():
            if relpath not in base_files:
                added.append(relpath)
            elif info['hash'] != base_files[relpath].get('hash'):
                changed.append(relpath)
        
        for relpath in base_files:
            if relpath not in current_files:
                deleted.append(relpath)
        
        # 創建差分包
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = name or f"beidou_diff_{timestamp}"
        
        archive_path = self.backup_dir / f"{name}.tar.gz"
        manifest_path = self.backup_dir / f"{name}_manifest.json"
        
        print(f"[Backup] 差分備份: +{len(added)} 新增, ~{len(changed)} 變更, -{len(deleted)} 刪除")
        
        with tarfile.open(archive_path, "w:gz") as tar:
            for relpath in added + changed:
                filepath = self.project_root / relpath
                tar.add(filepath, arcname=relpath)
        
        manifest = {
            'name': name,
            'type': 'diff',
            'base': base_manifest['name'],
            'created': datetime.now().isoformat(),
            'added': added,
            'changed': changed,
            'deleted': deleted,
            'archive_size': archive_path.stat().st_size
        }
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"[Backup] 差分完成: {archive_path}")
        
        return archive_path, manifest
    
    def list_backups(self) -> List[dict]:
        """列出所有備份"""
        backups = []
        for manifest_path in self.backup_dir.glob("*_manifest.json"):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                manifest['manifest_path'] = str(manifest_path)
                backups.append(manifest)
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def notify_telegram(self, manifest: dict) -> bool:
        """發送 Telegram 通知"""
        import urllib.request
        import urllib.parse
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8080151081:AAEV7amkwA7l2VEKteah7r2kyMEcWhI8NUc')
        chat_id = os.getenv('TELEGRAM_CHAT_ID', '5965951659')
        
        backup_type = "完整" if manifest['type'] == 'full' else "差分"
        size_mb = manifest['archive_size'] / 1024 / 1024
        
        if manifest['type'] == 'full':
            text = f"""📦 *北斗命數 - {backup_type}備份完成*

名稱: `{manifest['name']}`
文件數: {manifest['file_count']}
大小: {size_mb:.2f} MB
時間: {manifest['created'][:19]}

@星殼"""
        else:
            text = f"""📦 *北斗命數 - {backup_type}備份完成*

名稱: `{manifest['name']}`
基準: `{manifest['base']}`
新增: {len(manifest['added'])} 個
變更: {len(manifest['changed'])} 個
刪除: {len(manifest['deleted'])} 個
大小: {size_mb:.2f} MB

@星殼"""
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = urllib.parse.urlencode({
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }).encode()
            
            req = urllib.request.Request(url, data=data)
            urllib.request.urlopen(req, timeout=10)
            print("[Backup] Telegram 通知已發送")
            return True
        except Exception as e:
            print(f"[Backup] Telegram 通知失敗: {e}")
            return False


def run_backup(diff: bool = False, notify: bool = True) -> dict:
    """執行備份"""
    bs = BackupService()
    
    if diff:
        # 找最新的完整備份作為基準
        backups = bs.list_backups()
        full_backups = [b for b in backups if b['type'] == 'full']
        
        if not full_backups:
            print("[Backup] 無完整備份，執行完整備份")
            archive_path, manifest = bs.create_full_backup()
        else:
            base_manifest_path = Path(full_backups[0]['manifest_path'])
            archive_path, manifest = bs.create_diff_backup(base_manifest_path)
    else:
        archive_path, manifest = bs.create_full_backup()
    
    if notify:
        bs.notify_telegram(manifest)
    
    return {
        'success': True,
        'archive': str(archive_path),
        'manifest': manifest
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='北斗命數備份工具')
    parser.add_argument('--diff', action='store_true', help='差分備份')
    parser.add_argument('--no-notify', action='store_true', help='不發送通知')
    parser.add_argument('--list', action='store_true', help='列出備份')
    
    args = parser.parse_args()
    
    if args.list:
        bs = BackupService()
        backups = bs.list_backups()
        print(f"\n=== 備份列表 ({len(backups)}) ===")
        for b in backups[:10]:
            print(f"  {b['type']:4} | {b['name']} | {b['created'][:19]}")
    else:
        result = run_backup(diff=args.diff, notify=not args.no_notify)
        print(f"\n結果: {result}")
