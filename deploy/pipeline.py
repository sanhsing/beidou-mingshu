"""
完整部署流程 Pipeline
deploy/pipeline.py | @織明 | 2026-02-17

流程: C備份 → B測試 → A部署 → 上線
PYLIB: backup, test_all, deploy, launch

使用方式:
  python deploy/pipeline.py              # 執行完整流程
  python deploy/pipeline.py --step C     # 只執行備份
  python deploy/pipeline.py --step B     # 只執行測試
  python deploy/pipeline.py --step A     # 只執行部署
  python deploy/pipeline.py --step L     # 只執行上線檢查
  python deploy/pipeline.py --dry-run    # 模擬執行
"""
import os
import sys
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field

# === 路徑設置 ===
PROJECT_ROOT = Path(__file__).parent.parent
DEPLOY_DIR = PROJECT_ROOT / "deploy"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(DEPLOY_DIR))

# === 常量 ===
TELEGRAM_BOT = '8080151081:AAEV7amkwA7l2VEKteah7r2kyMEcWhI8NUc'
TELEGRAM_CHAT = '5965951659'


class Step(Enum):
    """流程步驟"""
    C_BACKUP = 'C'
    B_TEST = 'B'
    A_DEPLOY = 'A'
    LAUNCH = 'L'


@dataclass
class StepResult:
    """步驟結果"""
    step: Step
    success: bool
    message: str
    duration: float
    details: Dict[str, Any] = field(default_factory=dict)


class Pipeline:
    """
    部署流程管道
    
    C備份 → B測試 → A部署 → 上線
    """
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.results: List[StepResult] = []
        self.start_time = None
        self.end_time = None
    
    # ═══════════════════════════════════════════════════════════
    # C: 備份
    # ═══════════════════════════════════════════════════════════
    
    def step_c_backup(self) -> StepResult:
        """C: 執行備份"""
        print("\n" + "═" * 60)
        print("  📦 C: 備份")
        print("═" * 60)
        
        start = time.time()
        
        if self.dry_run:
            print("  [DRY-RUN] 模擬備份...")
            time.sleep(0.5)
            return StepResult(
                step=Step.C_BACKUP,
                success=True,
                message="模擬備份完成",
                duration=time.time() - start
            )
        
        try:
            from backup import BackupService
            
            bs = BackupService()
            
            # 檢查是否有現有備份
            backups = bs.list_backups()
            full_backups = [b for b in backups if b['type'] == 'full']
            
            if full_backups:
                # 有完整備份，做差分備份
                print("  執行差分備份...")
                base_path = Path(full_backups[0]['manifest_path'])
                archive_path, manifest = bs.create_diff_backup(base_path)
                backup_type = 'diff'
            else:
                # 沒有完整備份，做完整備份
                print("  執行完整備份...")
                archive_path, manifest = bs.create_full_backup()
                backup_type = 'full'
            
            duration = time.time() - start
            size_mb = manifest['archive_size'] / 1024 / 1024
            
            return StepResult(
                step=Step.C_BACKUP,
                success=True,
                message=f"{backup_type}備份完成: {size_mb:.2f}MB",
                duration=duration,
                details={'archive': str(archive_path), 'manifest': manifest}
            )
            
        except Exception as e:
            return StepResult(
                step=Step.C_BACKUP,
                success=False,
                message=f"備份失敗: {e}",
                duration=time.time() - start
            )
    
    # ═══════════════════════════════════════════════════════════
    # B: 測試
    # ═══════════════════════════════════════════════════════════
    
    def step_b_test(self) -> StepResult:
        """B: 執行測試"""
        print("\n" + "═" * 60)
        print("  🧪 B: 測試")
        print("═" * 60)
        
        start = time.time()
        
        if self.dry_run:
            print("  [DRY-RUN] 模擬測試...")
            time.sleep(0.5)
            return StepResult(
                step=Step.B_TEST,
                success=True,
                message="模擬測試通過",
                duration=time.time() - start,
                details={'passed': 20, 'failed': 0}
            )
        
        try:
            from test_all import run_all_tests, generate_report
            
            summary = run_all_tests()
            
            # 生成報告
            generate_report(summary)
            
            duration = time.time() - start
            success = summary['failed'] == 0
            
            return StepResult(
                step=Step.B_TEST,
                success=success,
                message=f"測試完成: {summary['passed']}/{summary['total']} 通過",
                duration=duration,
                details=summary
            )
            
        except Exception as e:
            import traceback
            return StepResult(
                step=Step.B_TEST,
                success=False,
                message=f"測試失敗: {e}",
                duration=time.time() - start,
                details={'error': traceback.format_exc()}
            )
    
    # ═══════════════════════════════════════════════════════════
    # A: 部署
    # ═══════════════════════════════════════════════════════════
    
    def step_a_deploy(self) -> StepResult:
        """A: 準備部署配置"""
        print("\n" + "═" * 60)
        print("  🚀 A: 部署")
        print("═" * 60)
        
        start = time.time()
        
        if self.dry_run:
            print("  [DRY-RUN] 模擬部署準備...")
            time.sleep(0.5)
            return StepResult(
                step=Step.A_DEPLOY,
                success=True,
                message="模擬部署配置完成",
                duration=time.time() - start
            )
        
        try:
            from deploy import DeployService
            
            ds = DeployService()
            
            # 檢查前置條件
            prereq = ds.check_prerequisites()
            
            # 生成配置
            outputs = ds.prepare_all()
            
            duration = time.time() - start
            
            return StepResult(
                step=Step.A_DEPLOY,
                success=True,
                message=f"部署配置已生成 ({len(outputs)} 個文件)",
                duration=duration,
                details={
                    'prerequisites': prereq,
                    'outputs': {k: str(v) for k, v in outputs.items()}
                }
            )
            
        except Exception as e:
            return StepResult(
                step=Step.A_DEPLOY,
                success=False,
                message=f"部署準備失敗: {e}",
                duration=time.time() - start
            )
    
    # ═══════════════════════════════════════════════════════════
    # L: 上線檢查
    # ═══════════════════════════════════════════════════════════
    
    def step_launch(self, url: str = None) -> StepResult:
        """上線: 執行上線檢查"""
        print("\n" + "═" * 60)
        print("  🎯 上線檢查")
        print("═" * 60)
        
        start = time.time()
        
        if self.dry_run:
            print("  [DRY-RUN] 模擬上線檢查...")
            time.sleep(0.5)
            return StepResult(
                step=Step.LAUNCH,
                success=True,
                message="模擬上線檢查完成",
                duration=time.time() - start
            )
        
        try:
            from launch import LaunchChecklist, RollbackPlan
            
            cl = LaunchChecklist()
            
            # 自動檢查
            cl.auto_check()
            
            # 如果有 URL，驗證部署
            if url:
                cl.verify_deployment(url)
            
            # 生成回滾計劃
            RollbackPlan.save()
            
            # 獲取狀態
            status = cl.get_status()
            cl.print_status()
            
            duration = time.time() - start
            
            return StepResult(
                step=Step.LAUNCH,
                success=status['ready'],
                message=f"P0: {status['p0']['passed']}/{status['p0']['total']}, " +
                        f"P1: {status['p1']['passed']}/{status['p1']['total']}",
                duration=duration,
                details=status
            )
            
        except Exception as e:
            return StepResult(
                step=Step.LAUNCH,
                success=False,
                message=f"上線檢查失敗: {e}",
                duration=time.time() - start
            )
    
    # ═══════════════════════════════════════════════════════════
    # 完整流程
    # ═══════════════════════════════════════════════════════════
    
    def run_full_pipeline(self, url: str = None) -> Dict[str, Any]:
        """執行完整流程: C → B → A → 上線"""
        self.start_time = datetime.now()
        
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " " * 15 + "北斗命數 SaaS 部署流程" + " " * 15 + "║")
        print("║" + " " * 15 + "C備份 → B測試 → A部署 → 上線" + " " * 9 + "║")
        print("╚" + "═" * 58 + "╝")
        
        if self.dry_run:
            print("\n⚠️  DRY-RUN 模式：不會執行實際操作\n")
        
        # C: 備份
        result_c = self.step_c_backup()
        self.results.append(result_c)
        
        if not result_c.success:
            print(f"\n❌ 備份失敗，流程中止")
            return self._get_summary()
        
        # B: 測試
        result_b = self.step_b_test()
        self.results.append(result_b)
        
        if not result_b.success:
            print(f"\n❌ 測試失敗，流程中止")
            print("  提示: 請修復測試問題後重新執行")
            return self._get_summary()
        
        # A: 部署
        result_a = self.step_a_deploy()
        self.results.append(result_a)
        
        if not result_a.success:
            print(f"\n❌ 部署準備失敗，流程中止")
            return self._get_summary()
        
        # 上線檢查
        result_l = self.step_launch(url)
        self.results.append(result_l)
        
        self.end_time = datetime.now()
        
        return self._get_summary()
    
    def run_single_step(self, step: Step, url: str = None) -> StepResult:
        """執行單個步驟"""
        self.start_time = datetime.now()
        
        if step == Step.C_BACKUP:
            result = self.step_c_backup()
        elif step == Step.B_TEST:
            result = self.step_b_test()
        elif step == Step.A_DEPLOY:
            result = self.step_a_deploy()
        elif step == Step.LAUNCH:
            result = self.step_launch(url)
        else:
            raise ValueError(f"未知步驟: {step}")
        
        self.results.append(result)
        self.end_time = datetime.now()
        
        return result
    
    def _get_summary(self) -> Dict[str, Any]:
        """獲取流程摘要"""
        total_duration = sum(r.duration for r in self.results)
        all_success = all(r.success for r in self.results)
        
        return {
            'success': all_success,
            'total_duration': total_duration,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'steps': [
                {
                    'step': r.step.value,
                    'name': r.step.name,
                    'success': r.success,
                    'message': r.message,
                    'duration': r.duration
                }
                for r in self.results
            ]
        }
    
    def print_summary(self):
        """打印流程摘要"""
        summary = self._get_summary()
        
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " " * 20 + "流程執行摘要" + " " * 20 + "║")
        print("╠" + "═" * 58 + "╣")
        
        for step in summary['steps']:
            icon = "✅" if step['success'] else "❌"
            name = {'C': '備份', 'B': '測試', 'A': '部署', 'L': '上線'}[step['step']]
            print(f"║  {icon} {step['step']}: {name:8} │ {step['message'][:35]:35} ║")
        
        print("╠" + "═" * 58 + "╣")
        
        status = "✅ 全部成功" if summary['success'] else "❌ 有步驟失敗"
        print(f"║  狀態: {status:15} │ 總耗時: {summary['total_duration']:.2f}s" + " " * 15 + "║")
        print("╚" + "═" * 58 + "╝")
    
    def notify_telegram(self) -> bool:
        """發送 Telegram 通知"""
        summary = self._get_summary()
        
        step_lines = []
        for step in summary['steps']:
            icon = "✅" if step['success'] else "❌"
            name = {'C': '備份', 'B': '測試', 'A': '部署', 'L': '上線'}[step['step']]
            step_lines.append(f"{icon} {name}: {step['message'][:30]}")
        
        status = "✅ 成功" if summary['success'] else "❌ 失敗"
        
        text = f"""🚀 *北斗命數 SaaS - 部署流程*

{status}

{chr(10).join(step_lines)}

總耗時: {summary['total_duration']:.2f}s

@織明 @星殼"""
        
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT}/sendMessage"
            data = urllib.parse.urlencode({
                'chat_id': TELEGRAM_CHAT,
                'text': text,
                'parse_mode': 'Markdown'
            }).encode()
            
            req = urllib.request.Request(url, data=data)
            urllib.request.urlopen(req, timeout=10)
            print("\n📤 Telegram 通知已發送")
            return True
        except Exception as e:
            print(f"\n⚠️ Telegram 通知失敗: {e}")
            return False


# ═══════════════════════════════════════════════════════════════
# 快捷函數
# ═══════════════════════════════════════════════════════════════

def run_pipeline(dry_run: bool = False, notify: bool = True, url: str = None) -> Dict[str, Any]:
    """執行完整流程"""
    pipeline = Pipeline(dry_run=dry_run)
    summary = pipeline.run_full_pipeline(url=url)
    pipeline.print_summary()
    
    if notify and not dry_run:
        pipeline.notify_telegram()
    
    return summary


def run_step(step: str, dry_run: bool = False, notify: bool = True, url: str = None) -> StepResult:
    """執行單個步驟"""
    step_map = {
        'C': Step.C_BACKUP,
        'B': Step.B_TEST,
        'A': Step.A_DEPLOY,
        'L': Step.LAUNCH,
        '備份': Step.C_BACKUP,
        '測試': Step.B_TEST,
        '部署': Step.A_DEPLOY,
        '上線': Step.LAUNCH,
    }
    
    step_enum = step_map.get(step.upper())
    if not step_enum:
        raise ValueError(f"未知步驟: {step}. 可用: C/B/A/L")
    
    pipeline = Pipeline(dry_run=dry_run)
    result = pipeline.run_single_step(step_enum, url=url)
    pipeline.print_summary()
    
    if notify and not dry_run:
        pipeline.notify_telegram()
    
    return result


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='北斗命數 SaaS 部署流程',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python pipeline.py              # 執行完整流程
  python pipeline.py --step C     # 只執行備份
  python pipeline.py --step B     # 只執行測試
  python pipeline.py --step A     # 只執行部署
  python pipeline.py --step L     # 只執行上線檢查
  python pipeline.py --dry-run    # 模擬執行
  python pipeline.py --url https://example.com  # 驗證部署
        """
    )
    
    parser.add_argument('--step', type=str, choices=['C', 'B', 'A', 'L'],
                        help='執行特定步驟 (C=備份, B=測試, A=部署, L=上線)')
    parser.add_argument('--dry-run', action='store_true',
                        help='模擬執行，不實際操作')
    parser.add_argument('--no-notify', action='store_true',
                        help='不發送 Telegram 通知')
    parser.add_argument('--url', type=str,
                        help='部署 URL (用於上線驗證)')
    
    args = parser.parse_args()
    
    try:
        if args.step:
            result = run_step(
                step=args.step,
                dry_run=args.dry_run,
                notify=not args.no_notify,
                url=args.url
            )
            sys.exit(0 if result.success else 1)
        else:
            summary = run_pipeline(
                dry_run=args.dry_run,
                notify=not args.no_notify,
                url=args.url
            )
            sys.exit(0 if summary['success'] else 1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ 流程被中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
