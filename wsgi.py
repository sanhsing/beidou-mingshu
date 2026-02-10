#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wsgi.py - Gunicorn 入口
"""

from mingshu_api_unified_v2 import MingshuUnifiedAPIv2

# 創建 Flask app 實例
api = MingshuUnifiedAPIv2()
app = api.app

if __name__ == "__main__":
    app.run()
