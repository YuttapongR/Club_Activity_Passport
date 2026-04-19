import hashlib
import time
import random

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.core.database import get_db_connection

router = APIRouter()


@router.post("/checkin")
async def checkin(request: Request):
    """บันทึกเวลาเข้าร่วมกิจกรรม"""
    if 'student_id' not in request.session:
        return {'status': 'error', 'message': 'กรุณาเข้าสู่ระบบ'}

    data = await request.json()
    student_id = request.session['student_id']

    if not data or 'code' not in data:
        return {'status': 'error', 'message': 'กรุณาระบุรหัสกิจกรรม'}

    code = data['code']
    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'ไม่สามารถเชื่อมต่อฐานข้อมูลได้'}

    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Find activity by code
        cursor.execute("SELECT * FROM activities WHERE Checkin_Code = %s", (code,))
        activity = cursor.fetchone()

        if not activity:
            return {'status': 'error', 'message': 'รหัสกิจกรรมไม่ถูกต้อง'}

        activity_id = activity['Activity_ID']
        hours = activity['Hours_Given']

        # 2. Check if already checked in
        cursor.execute(
            "SELECT * FROM activity_checkins WHERE Activity_ID = %s AND Student_ID = %s",
            (activity_id, student_id)
        )
        if cursor.fetchone():
            return {'status': 'error', 'message': 'คุณได้บันทึกเวลาเข้าร่วมกิจกรรมนี้ไปแล้ว'}

        # 3. Transaction — record check-in + update hours
        conn.start_transaction()
        cursor.execute(
            "INSERT INTO activity_checkins (Activity_ID, Student_ID) VALUES (%s, %s)",
            (activity_id, student_id)
        )
        cursor.execute(
            "UPDATE user SET Total_Hours = IFNULL(Total_Hours, 0) + %s WHERE Student_ID = %s",
            (hours, student_id)
        )
        conn.commit()
        return {
            'status': 'success',
            'message': f'บันทึกเวลาสำเร็จ! คุณได้รับ {hours} ชั่วโมง'
        }
    except Exception:
        conn.rollback()
        return {'status': 'error', 'message': 'เกิดข้อผิดพลาดในการบันทึกข้อมูล'}
    finally:
        cursor.close()
        conn.close()


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

    # Generate unique 6-digit checkin code
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
        # Delete checkins first due to FK constraints
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
def get_activities(club_id: str = None):
    """ดึงรายการกิจกรรมทั้งหมด (filter by club_id ได้)"""
    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'ไม่สามารถเชื่อมต่อฐานข้อมูลได้'}

    cursor = conn.cursor(dictionary=True)
    try:
        if club_id:
            cursor.execute(
                "SELECT * FROM activities WHERE Club_ID = %s ORDER BY Activity_Date DESC",
                (club_id,)
            )
        else:
            cursor.execute("SELECT * FROM activities ORDER BY Activity_Date DESC")

        activities = cursor.fetchall()

        # Convert Decimal/datetime to JSON-serializable types
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
        # 1. Get user total hours
        cursor.execute("SELECT Total_Hours FROM user WHERE Student_ID = %s", (student_id,))
        user_data = cursor.fetchone()
        total_hours = float(user_data['Total_Hours']) if user_data and user_data['Total_Hours'] else 0

        # 2. Get activities user checked into
        sql = """SELECT a.Activity_Name, a.Hours_Given, c.Checkin_Time, cl.Name_Club
                 FROM activity_checkins c
                 JOIN activities a ON c.Activity_ID = a.Activity_ID
                 LEFT JOIN club cl ON a.Club_ID = cl.Club_ID
                 WHERE c.Student_ID = %s
                 ORDER BY c.Checkin_Time DESC"""
        cursor.execute(sql, (student_id,))
        history = cursor.fetchall()

        # Convert types for JSON serialization
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
