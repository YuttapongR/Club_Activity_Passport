import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.core.config import SMTP_CONFIG

logger = logging.getLogger(__name__)


def send_activity_notification(recipients: list[dict], activity_name: str, club_name: str, activity_date: str):
    """
    ส่ง email แจ้งเตือนกิจกรรมให้สมาชิกชมรม

    Args:
        recipients: [{'email': 'xx@xx.com', 'name': 'ชื่อ'}]
        activity_name: ชื่อกิจกรรม
        club_name: ชื่อชมรม
        activity_date: วันที่กิจกรรม
    """
    smtp_user = SMTP_CONFIG['user']
    smtp_pass = SMTP_CONFIG['password']

    if not smtp_user or not smtp_pass:
        logger.warning("SMTP credentials not configured — skipping email notifications")
        return {'sent': 0, 'skipped': len(recipients), 'reason': 'SMTP not configured'}

    sent = 0
    failed = 0

    try:
        # เพิ่ม timeout 10 วินาที ป้องกันค้าง
        server = smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port'], timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)

        for person in recipients:
            email = person.get('email', '').strip()
            name = person.get('name', 'สมาชิก')

            if not email:
                failed += 1
                continue

            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = f"📢 แจ้งเตือนกิจกรรม: {activity_name}"
                msg['From'] = f"{SMTP_CONFIG['sender_name']} <{smtp_user}>"
                msg['To'] = email
                # ... (html_body as before)

                html_body = f"""
                <div style="font-family: 'Segoe UI', Tahoma, sans-serif; max-width: 500px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 16px;">
                    <div style="background: linear-gradient(135deg, #2563eb, #4f46e5); color: white; padding: 24px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
                        <h1 style="margin: 0; font-size: 20px;">📢 แจ้งเตือนกิจกรรม</h1>
                    </div>
                    <p style="color: #334155;">สวัสดีคุณ <strong>{name}</strong>,</p>
                    <p style="color: #334155;">คุณมีกิจกรรมที่ต้องเข้าร่วม:</p>
                    <div style="background: #f1f5f9; padding: 16px; border-radius: 12px; margin: 16px 0;">
                        <p style="margin: 4px 0; color: #1e293b;"><strong>🎯 กิจกรรม:</strong> {activity_name}</p>
                        <p style="margin: 4px 0; color: #1e293b;"><strong>🏢 ชมรม:</strong> {club_name}</p>
                        <p style="margin: 4px 0; color: #1e293b;"><strong>📅 วันที่:</strong> {activity_date}</p>
                    </div>
                    <p style="color: #64748b; font-size: 12px; text-align: center; margin-top: 24px;">
                        — ClubHub Management System
                    </p>
                </div>
                """

                msg.attach(MIMEText(html_body, 'html', 'utf-8'))
                server.sendmail(smtp_user, email, msg.as_string())
                sent += 1
            except Exception as e:
                logger.error(f"Failed to send email to {email}: {e}")
                failed += 1

        server.quit()
    except Exception as e:
        logger.error(f"SMTP connection error: {e}")
        return {'sent': sent, 'failed': failed, 'error': str(e)}

    return {'sent': sent, 'failed': failed}


def send_checkin_notification(recipients: list[dict], activity_name: str, hours: float):
    """
    ส่ง email แจ้งเตือนเมื่อ Admin บันทึกชั่วโมงให้แล้ว

    Args:
        recipients: [{'email': 'xx@xx.com', 'name': 'ชื่อ'}]
        activity_name: ชื่อกิจกรรม
        hours: จำนวนชั่วโมงที่ได้รับ
    """
    smtp_user = SMTP_CONFIG['user']
    smtp_pass = SMTP_CONFIG['password']

    if not smtp_user or not smtp_pass:
        return {'sent': 0, 'skipped': len(recipients), 'reason': 'SMTP not configured'}

    sent = 0
    failed = 0

    try:
        server = smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port'], timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)

        for person in recipients:
            email = person.get('email', '').strip()
            name = person.get('name', 'สมาชิก')

            if not email:
                failed += 1
                continue

            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = f"✅ บันทึกชั่วโมงสำเร็จ: {activity_name}"
                msg['From'] = f"{SMTP_CONFIG['sender_name']} <{smtp_user}>"
                msg['To'] = email

                html_body = f"""
                <div style="font-family: 'Segoe UI', Tahoma, sans-serif; max-width: 500px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 16px;">
                    <div style="background: linear-gradient(135deg, #059669, #10b981); color: white; padding: 24px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
                        <h1 style="margin: 0; font-size: 20px;">✅ บันทึกชั่วโมงสำเร็จ!</h1>
                    </div>
                    <p style="color: #334155;">สวัสดีคุณ <strong>{name}</strong>,</p>
                    <p style="color: #334155;">Admin ได้บันทึกชั่วโมงกิจกรรมให้คุณแล้ว:</p>
                    <div style="background: #f0fdf4; padding: 16px; border-radius: 12px; margin: 16px 0; text-align: center;">
                        <p style="margin: 4px 0; color: #166534; font-size: 18px;"><strong>{activity_name}</strong></p>
                        <p style="margin: 8px 0; color: #15803d; font-size: 28px; font-weight: bold;">+{hours} ชั่วโมง</p>
                    </div>
                    <p style="color: #64748b; font-size: 12px; text-align: center; margin-top: 24px;">
                        — ClubHub Management System
                    </p>
                </div>
                """

                msg.attach(MIMEText(html_body, 'html', 'utf-8'))
                server.sendmail(smtp_user, email, msg.as_string())
                sent += 1
            except Exception as e:
                logger.error(f"Failed to send email to {email}: {e}")
                failed += 1

        server.quit()
    except Exception as e:
        logger.error(f"SMTP connection error: {e}")
        return {'sent': sent, 'failed': failed, 'error': str(e)}

    return {'sent': sent, 'failed': failed}
