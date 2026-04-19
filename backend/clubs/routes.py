import os
import time
import hashlib
import secrets

from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse

from backend.core.database import get_db_connection

router = APIRouter()

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/create", response_class=HTMLResponse)
async def create_club(
    request: Request,
    club_name: str = Form(...),
    description: str = Form(""),
    category: str = Form(...),
    max_members: str = Form(""),
    saveclub: str = Form(None),
    club_image: UploadFile = File(None),
):
    """สร้างชมรมใหม่ — รับ form data + file upload"""
    member = max_members if max_members else 'ไม่จำกัด'
    image = 'default_club.png'

    # จัดการการอัปโหลดไฟล์ภาพ
    if club_image and club_image.filename:
        if allowed_file(club_image.filename):
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            ext = club_image.filename.rsplit('.', 1)[1].lower()
            new_filename = f"{int(time.time())}_{secrets.token_hex(4)}.{ext}"
            filepath = os.path.join(UPLOAD_DIR, new_filename)
            try:
                contents = await club_image.read()
                with open(filepath, "wb") as f:
                    f.write(contents)
                image = new_filename
            except Exception:
                return HTMLResponse("<script>alert('ไม่สามารถย้ายไฟล์ไปยังโฟลเดอร์เป้าหมายได้ กรุณาลองใหม่อีกครั้ง'); window.history.back();</script>")
        else:
            return HTMLResponse("<script>alert('รองรับเฉพาะไฟล์รูปภาพ (JPG, PNG, GIF) เท่านั้น'); window.history.back();</script>")

    conn = get_db_connection()
    if not conn:
        return HTMLResponse("<script>alert('ไม่สามารถเชื่อมต่อฐานข้อมูลได้'); window.history.back();</script>")

    cursor = conn.cursor()
    try:
        sql = """INSERT INTO club (Name_Club, Description, Club_type, Member, Club_Image)
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (club_name, description, category, member, image))
        conn.commit()
        return HTMLResponse("<script>alert('สร้างชมรมสำเร็จ'); window.location.href='/frontend/admin/Admin.html';</script>")
    except Exception as e:
        conn.rollback()
        error_msg = str(e).replace("'", "\\'")
        return HTMLResponse(f"<script>alert('สร้างชมรมไม่สำเร็จ: {error_msg}'); window.history.back();</script>")
    finally:
        cursor.close()
        conn.close()


@router.get("/delete", response_class=HTMLResponse)
def delete_club(id: str = None):
    """ลบชมรม — รับ id จาก query string"""
    if not id:
        return HTMLResponse("Invalid request")

    conn = get_db_connection()
    if not conn:
        return HTMLResponse("<script>alert('ไม่สามารถเชื่อมต่อฐานข้อมูลได้'); window.history.back();</script>")

    cursor = conn.cursor(dictionary=True)
    try:
        # ดึงข้อมูลเพื่อลบรูปภาพ (ถ้ามี)
        cursor.execute("SELECT Club_Image FROM club WHERE Club_ID = %s", (id,))
        row = cursor.fetchone()
        if row and row.get('Club_Image'):
            img_path = os.path.join(UPLOAD_DIR, row['Club_Image'])
            if os.path.exists(img_path):
                os.remove(img_path)

        cursor.execute("DELETE FROM club WHERE Club_ID = %s", (id,))
        conn.commit()
        return HTMLResponse("<script>alert('ลบชมรมสำเร็จ'); window.location.href='/frontend/admin/Admin.html';</script>")
    except Exception:
        conn.rollback()
        return HTMLResponse("<script>alert('ลบชมรมไม่สำเร็จ'); window.location.href='/frontend/admin/Admin.html';</script>")
    finally:
        cursor.close()
        conn.close()


@router.get("/list")
def get_clubs():
    """ดึงรายชื่อชมรมทั้งหมด"""
    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'DB connection failed'}

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM club ORDER BY Club_ID DESC")
        clubs = cursor.fetchall()
        return {'status': 'success', 'data': clubs}
    finally:
        cursor.close()
        conn.close()


@router.get("/detail")
def get_club_detail(request: Request, club_id: str = None):
    """ดึงรายละเอียดชมรม + สถานะการเป็นสมาชิก"""
    if not club_id:
        return {'status': 'error', 'message': 'Missing club_id'}

    student_id = request.session.get('student_id')
    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'DB connection failed'}

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM club WHERE Club_ID = %s", (club_id,))
        club = cursor.fetchone()

        if not club:
            return {'status': 'error', 'message': 'ไม่พบข้อมูลชมรม'}

        is_member = False
        current_members = 0

        try:
            if student_id:
                cursor.execute(
                    "SELECT Member_ID FROM membership WHERE Student_ID = %s AND Club_ID = %s",
                    (student_id, club_id)
                )
                if cursor.fetchone():
                    is_member = True

            cursor.execute("SELECT COUNT(*) as total FROM membership WHERE Club_ID = %s", (club_id,))
            count_row = cursor.fetchone()
            if count_row:
                current_members = count_row['total']
        except Exception:
            pass

        return {
            'status': 'success',
            'data': club,
            'is_member': is_member,
            'current_members': current_members
        }
    finally:
        cursor.close()
        conn.close()


@router.get("/members")
def get_club_members(request: Request, club_id: str = None):
    """ดึงรายชื่อสมาชิกชมรม (Admin เท่านั้น)"""
    if request.session.get('role') != 'admin':
        return {'status': 'error', 'message': 'Unauthorized access'}

    if not club_id:
        return {'status': 'error', 'message': 'Missing club_id'}

    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'DB connection failed'}

    cursor = conn.cursor(dictionary=True)
    try:
        sql = """SELECT u.Student_ID, u.Username, m.Join_Date
                 FROM membership m
                 JOIN user u ON m.Student_ID = u.Student_ID
                 WHERE m.Club_ID = %s"""
        cursor.execute(sql, (club_id,))
        members = cursor.fetchall()

        for m in members:
            for key, val in m.items():
                if hasattr(val, 'isoformat'):
                    m[key] = val.isoformat()

        return {'status': 'success', 'data': members}
    finally:
        cursor.close()
        conn.close()


@router.get("/roles")
def get_roles(request: Request, remove_id: str = None):
    """จัดการสิทธิ์ Admin — ดูรายการ Admin / ลบสิทธิ์ Admin"""
    if request.session.get('role') != 'admin':
        return {'status': 'error', 'message': 'Unauthorized access'}

    # ส่วนของการลบสิทธิ์
    if remove_id:
        if remove_id == request.session.get('student_id'):
            return {'status': 'error', 'message': 'ไม่สามารถลบสิทธิ์ตัวเองได้'}

        conn = get_db_connection()
        if not conn:
            return {'status': 'error', 'message': 'DB connection failed'}

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE user SET Role = 'user' WHERE Student_ID = %s", (remove_id,))
            conn.commit()
            return {'status': 'success', 'message': 'ปรับสิทธิ์เรียบร้อยแล้ว'}
        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': f'เกิดข้อผิดพลาด: {e}'}
        finally:
            cursor.close()
            conn.close()

    # ส่วนของการแสดงข้อมูล Admin
    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'DB connection failed'}

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT Student_ID, Username, Role FROM user WHERE Role = 'admin'")
        roles = cursor.fetchall()
        return {'status': 'success', 'data': roles}
    finally:
        cursor.close()
        conn.close()


@router.post("/issue_certs")
async def issue_certs(request: Request):
    """ออกใบรับรองให้สมาชิก (Admin เท่านั้น)"""
    if request.session.get('role') != 'admin':
        return {'status': 'error', 'message': 'Unauthorized access'}

    data = await request.json()
    if not data or 'club_id' not in data or 'student_ids' not in data:
        return {'status': 'error', 'message': 'Invalid data provided'}

    club_id = data['club_id']
    student_ids = data['student_ids']

    if not isinstance(student_ids, list):
        return {'status': 'error', 'message': 'Invalid data provided'}

    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'DB connection failed'}

    cursor = conn.cursor(dictionary=True)
    success_count = 0

    try:
        for sid in student_ids:
            raw = hashlib.md5(f"{sid}{time.time()}".encode()).hexdigest()[:8].upper()
            cert_code = f"CERT-{time.strftime('%Y')}-{raw}"

            cursor.execute(
                "SELECT Cert_ID FROM certificates WHERE Student_ID = %s AND Club_ID = %s",
                (sid, club_id)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO certificates (Student_ID, Club_ID, Cert_Code) VALUES (%s, %s, %s)",
                    (sid, club_id, cert_code)
                )
                success_count += 1

        conn.commit()
        return {
            'status': 'success',
            'message': f'ออกใบรับรองสำเร็จ {success_count} รายการ',
            'count': success_count
        }
    except Exception as e:
        conn.rollback()
        return {'status': 'error', 'message': str(e)}
    finally:
        cursor.close()
        conn.close()
