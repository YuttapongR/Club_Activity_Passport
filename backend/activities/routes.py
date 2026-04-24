import hashlib
import time
import random

from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from backend.core.database import get_db_connection
from backend.core.email_service import send_checkin_notification, send_activity_notification

router = APIRouter()


# =============================================================================
# Admin: บันทึกเวลาให้สมาชิก (แทนระบบรหัสเดิม)
# =============================================================================

@router.post("/admin_checkin")
async def admin_checkin(request: Request, background_tasks: BackgroundTasks):
    """Admin เลือกสมาชิกที่มาเข้าร่วม แล้วบันทึกชั่วโมงให้"""
    if request.session.get('role') != 'admin':
        return {'status': 'error', 'message': 'Unauthorized'}

    try:
        data = await request.json()
        activity_id = data.get('activity_id')
        student_ids = data.get('student_ids')

        if not activity_id or not student_ids:
            return {'status': 'error', 'message': 'ข้อมูลไม่ครบถ้วน'}

        if not isinstance(student_ids, list) or len(student_ids) == 0:
            return {'status': 'error', 'message': 'กรุณาเลือกสมาชิกอย่างน้อย 1 คน'}

        conn = get_db_connection()
        if not conn:
            return {'status': 'error', 'message': 'ไม่สามารถเชื่อมต่อฐานข้อมูลได้'}

        cursor = conn.cursor(dictionary=True)
        try:
            # ปิด autocommit เพื่อเริ่ม Transaction แบบ Manual
            # วิธีนี้จะชัวร์กว่า start_transaction() ในบางเวอร์ชัน
            conn.autocommit = False

            # 1. ดึงข้อมูลกิจกรรม
            cursor.execute("SELECT Hours_Given, Activity_Name FROM activities WHERE Activity_ID = %s", (activity_id,))
            activity = cursor.fetchone()
            if not activity:
                return {'status': 'error', 'message': 'ไม่พบกิจกรรมนี้'}

            hours = activity['Hours_Given']
            activity_name = activity['Activity_Name']

            # 2. บันทึกเวลาให้แต่ละคน
            success_count = 0
            already_count = 0
            email_recipients = []

            for sid in student_ids:
                # เช็คว่าบันทึกไปแล้วหรือยัง
                cursor.execute(
                    "SELECT Checkin_ID FROM activity_checkins WHERE Activity_ID = %s AND Student_ID = %s",
                    (activity_id, sid)
                )
                if cursor.fetchone():
                    already_count += 1
                    continue

                # บันทึก checkin
                cursor.execute(
                    "INSERT INTO activity_checkins (Activity_ID, Student_ID) VALUES (%s, %s)",
                    (activity_id, sid)
                )
                
                # อัพเดทชั่วโมง
                cursor.execute(
                    "UPDATE user SET Total_Hours = IFNULL(Total_Hours, 0) + %s WHERE Student_ID = %s",
                    (hours, sid)
                )
                success_count += 1

                # ดึงข้อมูล email สำหรับแจ้งเตือน
                cursor.execute("SELECT Email, First_Name, Last_Name FROM user WHERE Student_ID = %s", (sid,))
                user = cursor.fetchone()
                if user and user.get('Email'):
                    email_recipients.append({
                        'email': user['Email'],
                        'name': f"{user.get('First_Name', '')} {user.get('Last_Name', '')}"
                    })

            # ยืนยันข้อมูลทั้งหมด
            conn.commit()

            # 3. ส่ง email ใน background
            if email_recipients:
                background_tasks.add_task(send_checkin_notification, email_recipients, activity_name, float(hours))

            return {
                'status': 'success',
                'message': f'บันทึกเวลาสำเร็จ {success_count} คน' + (f' (มีอยู่แล้ว {already_count} คน)' if already_count else ''),
                'email_queued': len(email_recipients)
            }
        except Exception as inner_e:
            try: conn.rollback()
            except: pass
            print(f"DB Error: {inner_e}")
            return {'status': 'error', 'message': f'ฐานข้อมูลผิดพลาด: {inner_e}'}
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Server Error: {e}")
        return {'status': 'error', 'message': f'เกิดข้อผิดพลาดของระบบ: {e}'}


# =============================================================================
# Admin: ดึงรายชื่อสมาชิก + สถานะเช็คอิน
# =============================================================================

@router.get("/attendees")
def get_attendees(request: Request, activity_id: str = None):
    """ดึงรายชื่อสมาชิกชมรมที่ผูกกับกิจกรรม พร้อมสถานะว่าเช็คอินหรือยัง"""
    if request.session.get('role') != 'admin':
        return {'status': 'error', 'message': 'Unauthorized'}

    if not activity_id:
        return {'status': 'error', 'message': 'Missing activity_id'}

    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'DB connection failed'}

    cursor = conn.cursor(dictionary=True)
    try:
        # ดึง Club_ID ของกิจกรรมนี้
        cursor.execute("SELECT Club_ID FROM activities WHERE Activity_ID = %s", (activity_id,))
        act = cursor.fetchone()
        if not act:
            return {'status': 'error', 'message': 'ไม่พบกิจกรรมนี้'}

        club_id = act['Club_ID']

        # ดึงสมาชิกที่กดเข้าร่วมกิจกรรมนี้แล้ว (จาก activity_registrations) + สถานะ checkin
        sql = """
            SELECT u.Student_ID, u.Username, u.First_Name, u.Last_Name, u.Email,
                   CASE WHEN ac.Checkin_ID IS NOT NULL THEN 1 ELSE 0 END AS checked_in
            FROM activity_registrations ar
            JOIN user u ON ar.Student_ID = u.Student_ID
            LEFT JOIN activity_checkins ac ON ac.Student_ID = u.Student_ID AND ac.Activity_ID = %s
            WHERE ar.Activity_ID = %s
            ORDER BY u.Student_ID
        """
        cursor.execute(sql, (activity_id, activity_id))
        members = cursor.fetchall()

        return {'status': 'success', 'data': members, 'count': len(members)}
    finally:
        cursor.close()
        conn.close()


# =============================================================================
# Admin: ส่ง email แจ้งเตือนกิจกรรม
# =============================================================================

@router.post("/notify")
async def notify_activity(request: Request, background_tasks: BackgroundTasks):
    """ส่ง email แจ้งเตือนกิจกรรมให้สมาชิกชมรม"""
    if request.session.get('role') != 'admin':
        return {'status': 'error', 'message': 'Unauthorized'}

    data = await request.json()
    if not data or 'activity_id' not in data:
        return {'status': 'error', 'message': 'Missing activity_id'}

    activity_id = data['activity_id']

    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'DB connection failed'}

    cursor = conn.cursor(dictionary=True)
    try:
        sql = """SELECT a.*, c.Name_Club FROM activities a
                 LEFT JOIN club c ON a.Club_ID = c.Club_ID
                 WHERE a.Activity_ID = %s"""
        cursor.execute(sql, (activity_id,))
        act = cursor.fetchone()
        if not act:
            return {'status': 'error', 'message': 'ไม่พบกิจกรรมนี้'}

        cursor.execute("""
            SELECT u.Email, u.First_Name, u.Last_Name
            FROM membership m JOIN user u ON m.Student_ID = u.Student_ID
            WHERE m.Club_ID = %s AND u.Email IS NOT NULL AND u.Email != ''
        """, (act['Club_ID'],))
        members = cursor.fetchall()

        recipients = [{'email': m['Email'], 'name': f"{m['First_Name']} {m['Last_Name']}"} for m in members]

        activity_date = act['Activity_Date']
        if hasattr(activity_date, 'strftime'):
            activity_date = activity_date.strftime('%d/%m/%Y %H:%M')

        if recipients:
            background_tasks.add_task(
                send_activity_notification,
                recipients,
                act['Activity_Name'],
                act.get('Name_Club', 'ไม่ระบุชมรม'),
                str(activity_date)
            )

        return {
            'status': 'success',
            'message': f"กำลังส่งอีเมลแจ้งเตือนจำนวน {len(recipients)} ฉบับในเบื้องหลัง"
        }
    finally:
        cursor.close()
        conn.close()


# =============================================================================
# User: กิจกรรมวันนี้
# =============================================================================

@router.get("/today")
def get_today_activities(request: Request):
    """ดึงกิจกรรมที่มีวันนี้ สำหรับแจ้งเตือนบน Dashboard"""
    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'DB connection failed'}

    cursor = conn.cursor(dictionary=True)
    try:
        sql = """SELECT a.Activity_ID, a.Activity_Name, a.Activity_Date, a.Hours_Given,
                        c.Name_Club, c.Club_ID
                 FROM activities a
                 LEFT JOIN club c ON a.Club_ID = c.Club_ID
                 WHERE DATE(a.Activity_Date) = CURDATE()
                 ORDER BY a.Activity_Date ASC"""
        cursor.execute(sql)
        activities = cursor.fetchall()

        for act in activities:
            for key, val in act.items():
                if hasattr(val, 'isoformat'):
                    act[key] = val.isoformat()
                elif hasattr(val, '__float__'):
                    act[key] = float(val)

        return {'status': 'success', 'data': activities, 'count': len(activities)}
    finally:
        cursor.close()
        conn.close()


# =============================================================================
# Admin: CRUD กิจกรรม
# =============================================================================

@router.post("/create")
async def create_activity(request: Request):
    """สร้างกิจกรรมใหม่ (Admin เท่านั้น)"""
    if request.session.get('role') != 'admin':
        return {'status': 'error', 'message': 'Unauthorized'}

    data = await request.json()
    if not data or not all(k in data for k in ('activity_name', 'activity_date', 'hours')):
        return {'status': 'error', 'message': 'ข้อมูลไม่ครบถ้วน'}

    club_id = data.get('club_id', 0) or 0
    name = data['activity_name']
    desc = data.get('description', '')
    date = data['activity_date']
    hours = data['hours']

    # Generate unique 6-digit checkin code (เก็บไว้เป็น reference)
    raw = f"{time.time()}{random.randint(0, 999999)}"
    checkin_code = hashlib.md5(raw.encode()).hexdigest()[:6].upper()

    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'ไม่สามารถเชื่อมต่อฐานข้อมูลได้'}

    cursor = conn.cursor()
    try:
        sql = """INSERT INTO activities (Club_ID, Activity_Name, Description, Activity_Date, Hours_Given, Checkin_Code)
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (club_id, name, desc, date, hours, checkin_code))
        conn.commit()
        return {'status': 'success', 'message': 'เพิ่มกิจกรรมสำเร็จ', 'code': checkin_code}
    except Exception as e:
        conn.rollback()
        return {'status': 'error', 'message': str(e)}
    finally:
        cursor.close()
        conn.close()


@router.post("/delete")
async def delete_activity(request: Request):
    """ลบกิจกรรม (Admin เท่านั้น)"""
    if request.session.get('role') != 'admin':
        return {'status': 'error', 'message': 'Unauthorized'}

    data = await request.json()
    if not data or 'activity_id' not in data:
        return {'status': 'error', 'message': 'Missing activity_id'}

    activity_id = data['activity_id']
    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'ไม่สามารถเชื่อมต่อฐานข้อมูลได้'}

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM activity_checkins WHERE Activity_ID = %s", (activity_id,))
        cursor.execute("DELETE FROM activities WHERE Activity_ID = %s", (activity_id,))
        conn.commit()
        return {'status': 'success', 'message': 'ลบกิจกรรมเรียบร้อยแล้ว'}
    except Exception as e:
        conn.rollback()
        return {'status': 'error', 'message': str(e)}
    finally:
        cursor.close()
        conn.close()


@router.get("/list")
def get_activities(request: Request, club_id: str = None):
    """ดึงรายการกิจกรรมทั้งหมด พร้อมจำนวนผู้เข้าร่วม"""
    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'ไม่สามารถเชื่อมต่อฐานข้อมูลได้'}

    student_id = request.session.get('student_id')
    cursor = conn.cursor(dictionary=True)
    try:
        if club_id:
            sql = """
                SELECT a.*, 
                       (SELECT COUNT(*) FROM activity_registrations ar WHERE ar.Activity_ID = a.Activity_ID) as registered_count,
                       (SELECT COUNT(*) FROM activity_registrations ar WHERE ar.Activity_ID = a.Activity_ID AND ar.Student_ID = %s) as is_registered
                FROM activities a 
                WHERE a.Club_ID = %s 
                ORDER BY a.Activity_Date DESC
            """
            cursor.execute(sql, (student_id, club_id))
        else:
            sql = """
                SELECT a.*, 
                       (SELECT COUNT(*) FROM activity_registrations ar WHERE ar.Activity_ID = a.Activity_ID) as registered_count,
                       (SELECT COUNT(*) FROM activity_registrations ar WHERE ar.Activity_ID = a.Activity_ID AND ar.Student_ID = %s) as is_registered
                FROM activities a 
                ORDER BY a.Activity_Date DESC
            """
            cursor.execute(sql, (student_id,))

        activities = cursor.fetchall()

        for act in activities:
            for key, val in act.items():
                if hasattr(val, 'isoformat'):
                    act[key] = val.isoformat()
                elif hasattr(val, '__float__'):
                    act[key] = float(val)

        return {'status': 'success', 'data': activities}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    finally:
        cursor.close()
        conn.close()


@router.get("/summary")
def get_user_summary(request: Request):
    """ดึงข้อมูลสรุปชั่วโมงกิจกรรมของผู้ใช้"""
    if 'student_id' not in request.session:
        return {'status': 'error', 'message': 'Not logged in'}

    student_id = request.session['student_id']
    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'ไม่สามารถเชื่อมต่อฐานข้อมูลได้'}

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT Total_Hours FROM user WHERE Student_ID = %s", (student_id,))
        user_data = cursor.fetchone()
        total_hours = float(user_data['Total_Hours']) if user_data and user_data['Total_Hours'] else 0

        sql = """SELECT a.Activity_Name, a.Hours_Given, c.Checkin_Time, cl.Name_Club
                 FROM activity_checkins c
                 JOIN activities a ON c.Activity_ID = a.Activity_ID
                 LEFT JOIN club cl ON a.Club_ID = cl.Club_ID
                 WHERE c.Student_ID = %s
                 ORDER BY c.Checkin_Time DESC"""
        cursor.execute(sql, (student_id,))
        history = cursor.fetchall()

        for item in history:
            for key, val in item.items():
                if hasattr(val, 'isoformat'):
                    item[key] = val.isoformat()
                elif hasattr(val, '__float__'):
                    item[key] = float(val)

        return {
            'status': 'success',
            'total_hours': total_hours,
            'history': history
        }
    finally:
        cursor.close()
        conn.close()

# =============================================================================
# User: เข้าร่วมกิจกรรม
# =============================================================================

@router.post("/register")
async def register_activity(request: Request):
    """ลงทะเบียนเข้าร่วมกิจกรรม"""
    if 'student_id' not in request.session:
        return {'status': 'error', 'message': 'กรุณาเข้าสู่ระบบก่อน'}

    data = await request.json()
    activity_id = data.get('activity_id')
    if not activity_id:
        return {'status': 'error', 'message': 'ไม่พบรหัสกิจกรรม'}

    student_id = request.session['student_id']

    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'ไม่สามารถเชื่อมต่อฐานข้อมูลได้'}

    cursor = conn.cursor(dictionary=True)
    try:
        # Check if already registered
        cursor.execute("SELECT Registration_ID FROM activity_registrations WHERE Activity_ID = %s AND Student_ID = %s", (activity_id, student_id))
        if cursor.fetchone():
            return {'status': 'error', 'message': 'คุณได้เข้าร่วมกิจกรรมนี้ไปแล้ว'}

        # Insert registration
        cursor.execute("INSERT INTO activity_registrations (Activity_ID, Student_ID) VALUES (%s, %s)", (activity_id, student_id))
        conn.commit()
        return {'status': 'success', 'message': 'เข้าร่วมกิจกรรมสำเร็จ'}
    except Exception as e:
        conn.rollback()
        return {'status': 'error', 'message': str(e)}
    finally:
        cursor.close()
        conn.close()

