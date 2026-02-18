"""
健康檢查模組
M10.7 | @星殼 | 2026-02-17
"""
from fastapi import APIRouter
from datetime import datetime
import sqlite3
import os

router = APIRouter(tags=["health"])

@router.get("/api/health")
async def health_check():
    """系統健康檢查"""
    checks = {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'checks': {}
    }
    
    # 數據庫檢查
    try:
        conn = sqlite3.connect('beidou_unified.db')
        conn.execute('SELECT 1')
        conn.close()
        checks['checks']['database'] = 'ok'
    except Exception as e:
        checks['checks']['database'] = f'error: {str(e)}'
        checks['status'] = 'degraded'
    
    # 環境檢查
    checks['checks']['env'] = os.getenv('APP_ENV', 'development')
    
    return checks

@router.get("/api/health/live")
async def liveness():
    """存活檢查 (K8s)"""
    return {'status': 'alive'}

@router.get("/api/health/ready")
async def readiness():
    """就緒檢查 (K8s)"""
    try:
        conn = sqlite3.connect('beidou_unified.db')
        conn.execute('SELECT 1')
        conn.close()
        return {'status': 'ready'}
    except:
        return {'status': 'not_ready'}, 503
