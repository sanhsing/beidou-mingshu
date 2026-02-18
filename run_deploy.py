#!/usr/bin/env python3
"""
快捷部署腳本
run_deploy.py | @織明 | 2026-02-17

使用:
  python run_deploy.py              # 完整流程
  python run_deploy.py C            # 只備份
  python run_deploy.py B            # 只測試
  python run_deploy.py A            # 只部署
  python run_deploy.py L            # 只上線檢查
  python run_deploy.py --dry-run    # 模擬
"""
import sys
sys.path.insert(0, '.')

from deploy.pipeline import run_pipeline, run_step

if __name__ == "__main__":
    args = sys.argv[1:]
    
    dry_run = '--dry-run' in args
    if dry_run:
        args.remove('--dry-run')
    
    if args and args[0] in ['C', 'B', 'A', 'L']:
        run_step(args[0], dry_run=dry_run)
    else:
        run_pipeline(dry_run=dry_run)
