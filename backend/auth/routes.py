from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from backend.core.database import get_db_connection

router = APIRouter()


@router.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """ล็อกอิน — รับ form data (username, password)"""
    conn = get_db_connection()
    if not conn:
        return HTMLResponse("<script>alert('ไม่สามารถเชื่อมต่อฐานข้อมูลได้'); window.history.back();</script>")

    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM user WHERE (Username = %s OR Student_ID = %s) AND Password = %s"
        cursor.execute(sql, (username, username, password))
        row = cursor.fetchone()

        if row:
            # ล็อกอินสำเร็จ — เก็บข้อมูลลง session
            request.session['student_id'] = row['Student_ID']
            request.session['username'] = row['Username']
            request.session['firstname'] = row['First_Name']
            request.session['lastname'] = row['Last_Name']
            request.session['role'] = row.get('Role', 'user')

            return HTMLResponse("""<script>
                alert('เข้าสู่ระบบสำเร็จ');
                window.location.href = '/frontend/dashboard/main.html';
            </script>""")
        else:
            return HTMLResponse("""<script>
                alert('ชื่อผู้ใช้งาน หรือ รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง');
                window.history.back();
            </script>""")
    finally:
        cursor.close()
        conn.close()


@router.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    student_id: str = Form(...),
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    bt: str = Form(None),
):
    """สมัครสมาชิก — รับ form data"""
    if password != confirm_password:
        return HTMLResponse("<script>alert('รหัสผ่านไม่ตรงกัน'); window.history.back();</script>")

    conn = get_db_connection()
    if not conn:
        return HTMLResponse("<script>alert('ไม่สามารถเชื่อมต่อฐานข้อมูลได้'); window.history.back();</script>")

    cursor = conn.cursor()
    try:
        sql = """INSERT INTO user (Student_ID, Username, First_Name, Last_Name, Password, Phone, Email)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (student_id, username, firstname, lastname, password, phone, email))
        conn.commit()
        return HTMLResponse("<script>alert('สมัครสมาชิกสำเร็จ'); window.location.href='/frontend/auth/login.html';</script>")
    except Exception:
        conn.rollback()
        return HTMLResponse("<script>alert('สมัครสมาชิกไม่สำเร็จ'); window.history.back();</script>")
    finally:
        cursor.close()
        conn.close()


@router.get("/check")
def check_auth(request: Request):
    """ตรวจสอบสถานะ login"""
    if 'student_id' in request.session:
        return {
            'status': 'success',
            'role': request.session.get('role', 'user'),
            'username': request.session.get('username', '')
        }
    else:
        return {'status': 'error', 'message': 'Not logged in'}


@router.get("/logout")
def logout(request: Request):
    """ออกจากระบบ"""
    request.session.clear()
    return RedirectResponse(url="/frontend/auth/login.html")
