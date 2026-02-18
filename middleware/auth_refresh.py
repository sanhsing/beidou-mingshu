"""JWT Refresh Token | @星殼"""
from datetime import datetime, timedelta
import os
SECRET = os.getenv('SECRET_KEY', 'dev-secret')
def create_refresh_token(user_id): return f"refresh_{user_id}_{datetime.now().timestamp()}"
def verify_refresh_token(token): return {'user_id': 1} if token.startswith('refresh_') else None
