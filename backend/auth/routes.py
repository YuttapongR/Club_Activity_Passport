from flask import Blueprint, request, session, jsonify

from backend.core.database import get_db_connection

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """ล็อกอิน — รับ form data (username, password)"""
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    conn = get_db_connection()
    if not conn:
        return "<script>alert('ไม่สามารถเชื่อมต่อฐานข้อมูลได้'); window.history.back();</script>"

    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM user WHERE (Username = %s OR Student_ID = %s) AND Password = %s"
        cursor.execute(sql, (username, username, password))
        row = cursor.fetchone()

        if row:
            # ล็อกอินสำเร็จ — เก็บข้อมูลลง session
            session['student_id'] = row['Student_ID']
            session['username'] = row['Username']
            session['firstname'] = row['First_Name']
            session['lastname'] = row['Last_Name']
            session['role'] = row.get('Role', 'user')

            return """<script>
                alert('เข้าสู่ระบบสำเร็จ');
                window.location.href = '/frontend/dashboard/main.html';
            </script>"""
        else:
            return """<script>
                alert('ชื่อผู้ใช้งาน หรือ รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง');
                window.history.back();
            </script>"""
    finally:
        cursor.close()
        conn.close()


@auth_bp.route('/register', methods=['POST'])
def register():
    """สมัครสมาชิก — รับ form data"""
    student_id = request.form.get('student_id', '')
    username = request.form.get('username', '')
    firstname = request.form.get('firstname', '')
    lastname = request.form.get('lastname', '')
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')

    if password != confirm_password:
        return "<script>alert('รหัสผ่านไม่ตรงกัน'); window.history.back();</script>"

    conn = get_db_connection()
    if not conn:
        return "<script>alert('ไม่สามารถเชื่อมต่อฐานข้อมูลได้'); window.history.back();</script>"

    cursor = conn.cursor()
    try:
        sql = """INSERT INTO user (Student_ID, Username, First_Name, Last_Name, Password, Phone, Email)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (student_id, username, firstname, lastname, password, phone, email))
        conn.commit()
        return "<script>alert('สมัครสมาชิกสำเร็จ'); window.location.href='/frontend/auth/login.html';</script>"
    except Exception:
        conn.rollback()
        return "<script>alert('สมัครสมาชิกไม่สำเร็จ'); window.history.back();</script>"
    finally:
        cursor.close()
        conn.close()


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """ตรวจสอบสถานะ login"""
    if 'student_id' in session:
        return jsonify({
            'status': 'success',
            'role': session.get('role', 'user'),
            'username': session.get('username', '')
        })
    else:
        return jsonify({'status': 'error', 'message': 'Not logged in'})


@auth_bp.route('/logout', methods=['GET'])
def logout():
    """ออกจากระบบ"""
    session.clear()
    return redirect('/frontend/auth/login.html')
