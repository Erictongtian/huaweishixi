import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


def _send_email(to_email: str, subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    if settings.SMTP_SSL:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=context) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
    else:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())


async def send_verification_code(to_email: str, code: str) -> None:
    subject = "校园二手交易平台 - 验证码"
    html_body = f"""
    <div style="max-width:600px;margin:0 auto;font-family:'Microsoft YaHei',sans-serif;padding:20px;">
        <div style="background:linear-gradient(135deg,#0052FF,#4D7CFF);padding:30px;border-radius:12px 12px 0 0;text-align:center;">
            <h1 style="color:#fff;margin:0;font-size:24px;">校园二手交易平台</h1>
        </div>
        <div style="background:#fff;padding:30px;border:1px solid #e0e0e0;border-top:none;border-radius:0 0 12px 12px;">
            <p style="font-size:16px;color:#333;">您好！</p>
            <p style="font-size:16px;color:#333;">您正在注册校园二手交易平台账号，验证码为：</p>
            <div style="text-align:center;margin:30px 0;">
                <span style="font-size:36px;font-weight:700;color:#0052FF;letter-spacing:8px;font-family:monospace;">{code}</span>
            </div>
            <p style="font-size:14px;color:#999;">验证码5分钟内有效，如非本人操作请忽略。</p>
        </div>
    </div>
    """
    _send_email(to_email, subject, html_body)


async def send_verification_email(to_email: str, token: str) -> None:
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    subject = "校园二手交易平台 - 邮箱验证"
    html_body = f"""
    <div style="max-width:600px;margin:0 auto;font-family:'Microsoft YaHei',sans-serif;padding:20px;">
        <div style="background:linear-gradient(135deg,#0052FF,#4D7CFF);padding:30px;border-radius:12px 12px 0 0;text-align:center;">
            <h1 style="color:#fff;margin:0;font-size:24px;">校园二手交易平台</h1>
        </div>
        <div style="background:#fff;padding:30px;border:1px solid #e0e0e0;border-top:none;border-radius:0 0 12px 12px;">
            <p style="font-size:16px;color:#333;">您好！</p>
            <p style="font-size:16px;color:#333;">感谢您注册校园二手交易平台，请点击下方按钮完成邮箱验证：</p>
            <div style="text-align:center;margin:30px 0;">
                <a href="{verify_url}" style="background:linear-gradient(135deg,#0052FF,#4D7CFF);color:#fff;padding:12px 36px;border-radius:8px;text-decoration:none;font-size:16px;display:inline-block;">验证邮箱</a>
            </div>
            <p style="font-size:14px;color:#999;">如果按钮无法点击，请复制以下链接到浏览器打开：</p>
            <p style="font-size:14px;color:#0052FF;word-break:break-all;">{verify_url}</p>
            <p style="font-size:14px;color:#999;margin-top:30px;">此链接24小时内有效，如非本人操作请忽略。</p>
        </div>
    </div>
    """
    _send_email(to_email, subject, html_body)