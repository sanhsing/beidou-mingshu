"""
北斗命數 SaaS 部署工具包
deploy/__init__.py | @織明 | 2026-02-17

模組:
- backup: C 備份
- test_all: B 測試
- deploy: A 部署
- launch: 上線檢查
- pipeline: 完整流程

使用方式:
  from deploy import pipeline
  pipeline.run_pipeline()
  
  # 或單步執行
  pipeline.run_step('C')  # 備份
  pipeline.run_step('B')  # 測試
  pipeline.run_step('A')  # 部署
  pipeline.run_step('L')  # 上線
"""

__version__ = '1.0.0'
__author__ = '北斗命數團隊'

# 導出主要函數
from .pipeline import run_pipeline, run_step, Pipeline
from .backup import BackupService, run_backup
from .test_all import TestRunner, run_all_tests
from .deploy import DeployService, run_deploy
from .launch import LaunchChecklist, run_launch_check

__all__ = [
    'run_pipeline',
    'run_step',
    'Pipeline',
    'BackupService',
    'run_backup',
    'TestRunner',
    'run_all_tests',
    'DeployService',
    'run_deploy',
    'LaunchChecklist',
    'run_launch_check',
]
