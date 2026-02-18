"""
Email 服務模組
M7.1-M7.7 | @流祇 | 2026-02-17
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

class EmailService:
    """郵件服務"""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_pass = os.getenv('SMTP_PASS', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@beidou-mingshu.com')
        self.from_name = '北斗命數'
    
    def _send(self, to_email: str, subject: str, html_content: str) -> bool:
        """發送郵件"""
        if not self.smtp_user:
            print(f"[Email] 模擬發送: {to_email} - {subject}")
            return True
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"[Email] 發送失敗: {e}")
            return False
    
    def send_welcome(self, to_email: str, username: str) -> bool:
        """發送歡迎郵件"""
        html = f'''
        <div style="max-width:600px;margin:0 auto;font-family:sans-serif;">
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:30px;text-align:center;">
                <h1 style="color:white;margin:0;">🌟 歡迎加入北斗命數</h1>
            </div>
            <div style="padding:30px;background:#f8f9fa;">
                <p>親愛的 {username}，</p>
                <p>感謝您註冊北斗命數！我們已為您的帳戶贈送 <strong>50 點</strong>，可以免費體驗基礎命盤分析。</p>
                <div style="text-align:center;margin:30px 0;">
                    <a href="https://beidou-mingshu.com/dashboard" 
                       style="background:#667eea;color:white;padding:15px 30px;text-decoration:none;border-radius:8px;font-weight:bold;">
                        開始探索
                    </a>
                </div>
                <p style="color:#666;">如有任何問題，歡迎回覆此郵件或聯繫客服。</p>
            </div>
            <div style="padding:20px;text-align:center;color:#999;font-size:12px;">
                © 2026 北斗命數 | <a href="https://beidou-mingshu.com/legal/privacy">隱私政策</a>
            </div>
        </div>
        '''
        return self._send(to_email, '🌟 歡迎加入北斗命數！', html)
    
    def send_report_ready(self, to_email: str, username: str, report_name: str, report_url: str) -> bool:
        """發送報告完成通知"""
        html = f'''
        <div style="max-width:600px;margin:0 auto;font-family:sans-serif;">
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:30px;text-align:center;">
                <h1 style="color:white;margin:0;">📜 您的報告已準備好</h1>
            </div>
            <div style="padding:30px;background:#f8f9fa;">
                <p>親愛的 {username}，</p>
                <p>您的 <strong>{report_name}</strong> 已經生成完成，可以下載查看了！</p>
                <div style="text-align:center;margin:30px 0;">
                    <a href="{report_url}" 
                       style="background:#667eea;color:white;padding:15px 30px;text-decoration:none;border-radius:8px;font-weight:bold;">
                        查看報告
                    </a>
                </div>
            </div>
        </div>
        '''
        return self._send(to_email, f'📜 您的{report_name}已準備好', html)
    
    def send_payment_success(self, to_email: str, username: str, amount: int, credits: int) -> bool:
        """發送支付成功通知"""
        html = f'''
        <div style="max-width:600px;margin:0 auto;font-family:sans-serif;">
            <div style="background:linear-gradient(135deg,#22c55e,#16a34a);padding:30px;text-align:center;">
                <h1 style="color:white;margin:0;">✅ 支付成功</h1>
            </div>
            <div style="padding:30px;background:#f8f9fa;">
                <p>親愛的 {username}，</p>
                <p>您的支付已成功處理：</p>
                <div style="background:white;padding:20px;border-radius:8px;margin:20px 0;">
                    <p><strong>支付金額：</strong>NT${amount}</p>
                    <p><strong>獲得點數：</strong>{credits} 點</p>
                    <p><strong>交易時間：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                <p>點數已即時入帳，歡迎使用！</p>
            </div>
        </div>
        '''
        return self._send(to_email, '✅ 支付成功通知', html)
    
    def send_password_reset(self, to_email: str, reset_url: str) -> bool:
        """發送密碼重置郵件"""
        html = f'''
        <div style="max-width:600px;margin:0 auto;font-family:sans-serif;">
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:30px;text-align:center;">
                <h1 style="color:white;margin:0;">🔒 重置密碼</h1>
            </div>
            <div style="padding:30px;background:#f8f9fa;">
                <p>您收到此郵件是因為有人請求重置您的密碼。</p>
                <p>如果這不是您本人操作，請忽略此郵件。</p>
                <div style="text-align:center;margin:30px 0;">
                    <a href="{reset_url}" 
                       style="background:#667eea;color:white;padding:15px 30px;text-decoration:none;border-radius:8px;font-weight:bold;">
                        重置密碼
                    </a>
                </div>
                <p style="color:#999;font-size:12px;">此連結將在 24 小時後失效。</p>
            </div>
        </div>
        '''
        return self._send(to_email, '🔒 重置您的密碼', html)

# 單例
email_service = EmailService()

if __name__ == "__main__":
    es = EmailService()
    print("Email 服務模組已載入")
    print(f"SMTP: {es.smtp_host}:{es.smtp_port}")
    print(f"發送者: {es.from_email}")
