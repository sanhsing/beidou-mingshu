"""
模組整合腳本
將 M1-M3 新模組整合到主應用
"""
# 需要在 app.py 中加入的路由

INTEGRATION_CODE = '''
# === 新增模組整合 (M1-M3) ===

# M1: 法律頁面路由
from legal_routes import router as legal_router
app.include_router(legal_router)

# M2: 落地頁路由  
from landing_page import router as landing_router
app.include_router(landing_router)

# M3: 免費試算路由
from free_trial import router as free_router
app.include_router(free_router)
'''

print("請將以下代碼加入 app.py：")
print(INTEGRATION_CODE)
