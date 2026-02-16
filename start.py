#!/usr/bin/env python3
"""
北斗命數 MVP 啟動器
===================
一鍵啟動命理分析服務

用法:
    python start.py [port]
    
默認端口: 8000
"""

import sys
import os

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                   北斗命數 MVP v2.3                              ║
║                                                                  ║
║              四術統合 · 場論翻譯 · 去神秘化                      ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  前端頁面:  http://localhost:{port}                              ║
║  API文檔:   http://localhost:{port}/docs                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """.format(port=port))
    
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    main()
