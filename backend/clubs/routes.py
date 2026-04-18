import os
import time
import hashlib
import secrets

from flask import Blueprint, request, session, jsonify, redirect
from werkzeug.utils import secure_filename

from backend.core.database import get_db_connection

clubs_bp = Blueprint('clubs', __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@clubs_bp.route('/create', methods=['POST'])
def create_club():
    """สร้างชมรมใหม่ — รับ form data + file upload"""
    nameclub = request.form.get('club_name', '')
    desc = request.form.get('description', '')
    clubtype = request.form.get('category', '')
    member = request.form.get('max_members', '') or 'ไม่จำกัด'

    image = 'default_club.png'

    # จัดการการอัปโหลดไฟล์ภาพ
    if 'club_image' in request.files:
        file = request.files['club_image']
        if file and file.filename != '':
            if allowed_file(file.filename):
                # สร้างโฟลเดอร์ uploads ถ้ายังไม่มี
                os.makedirs(UPLOAD_DIR, exist_ok=True)

                ext = file.filename.rsplit('.', 1)[1].lower()
                new_filename = f"{int(time.time())}_{secrets.token_hex(4)}.{ext}"
                filepath = os.path.join(UPLOAD_DIR, new_filename)

                try:
                    file.save(filepath)
                    image = new_filename
                except Exception:
                    return "<script>alert('ไม่สามารถย้ายไฟล์ไปยังโฟลเดอร์เป้าหมายได้ กรุณาลองใหม่อีกครั้ง'); window.history.back();</script>"
            else:
                return "<script>alert('รองรับเฉพาะไฟล์รูปภาพ (JPG, PNG, GIF) เท่านั้น'); window.history.back();</script>"

    conn = get_db_connection()
    if not conn:
        return "<script>alert('ไม่สามารถเชื่อมต่อฐานข้อมูลได้'); window.history.back();</script>"

    cursor = conn.cursor()
    try:
        sql = """INSERT INTO club (Name_Club, Description, Club_type, Member, Club_Image)
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (nameclub, desc, clubtype, member, image))
        conn.commit()
        return "<script>alert('สร้างชมรมสำเร็จ'); window.location.href='/frontend/admin/Admin.html';</script>"
    except Exception as e:
        conn.rollback()
        error_msg = str(e).replace("'", "\\'")
        return f"<script>alert('สร้างชมรมไม่สำเร็จ: {error_msg}'); window.history.back();</script>"
    finally:
        cursor.close()
        conn.close()


@clubs_bp.route('/delete', methods=['GET'])
def delete_club():
    """ลบชมรม — รับ id จาก query string"""
    club_id = request.args.get('id')
    if not club_id:
        return "Invalid request"

    conn = get_db_connection()
    if not conn:
        return "<script>alert('ไม่สามารถเชื่อมต่อฐานข้อมูลได้'); window.history.back();</script>"

    cursor = conn.cursor(dictionary=True)
    try:
        # ดึงข้อมูลเพื่อลบรูปภาพ (ถ้ามี)
        cursor.execute("SELECT Club_Image FROM club WHERE Club_ID = %s", (club_id,))
        row = cursor.fetchone()
        if row and row.get('Club_Image'):
            img_path = os.path.join(UPLOAD_DIR, row['Club_Image'])
            if os.path.exists(img_path):
                os.remove(img_path)

        cursor.execute("DELETE FROM club WHERE Club_ID = %s", (club_id,))
        conn.commit()
        return "<script>alert('ลบชมรมสำเร็จ'); window.location.href='/frontend/admin/Admin.html';</script>"
    except Exception:
        conn.rollback()
        return "<script>alert('ลบชมรมไม่สำเร็จ'); window.location.href='/frontend/admin/Admin.html';</script>"
    finally:
        cursor.close()
        conn.close()


@clubs_bp.route('/list', methods=['GET'])
def get_clubs():
    """ดึงรายชื่อชมรมทั้งหมด"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB connection failed'})

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM club ORDER BY Club_ID DESC")
        clubs = cursor.fetchall()
        return jsonify({'status': 'success', 'data': clubs})
    finally:
        cursor.close()
        conn.close()


@clubs_bp.route('/detail', methods=['GET'])
def get_club_detail():
    """ดึงรายละเอียดชมรม + สถานะการเป็นสมาชิก"""
    club_id = request.args.get('club_id')
    if not club_id:
        return jsonify({'status': 'error', 'message': 'Missing club_id'})

    student_id = session.get('student_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB connection failed'})

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM club WHERE Club_ID = %s", (club_id,))
        club = cursor.fetchone()

        if not club:
            return jsonify({'status': 'error', 'message': 'ไม่พบข้อมูลชมรม'})

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
            # หากตาราง membership ยังไม่มี ให้ข้ามส่วนนี้ไปก่อน
            pass

        return jsonify({
            'status': 'success',
            'data': club,
            'is_member': is_member,
            'current_members': current_members
        })
    finally:
        cursor.close()
        conn.close()


@clubs_bp.route('/members', methods=['GET'])
def get_club_members():
    """ดึงรายชื่อสมาชิกชมรม (Admin เท่านั้น)"""
    if session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized access'})

    club_id = request.args.get('club_id')
    if not club_id:
        return jsonify({'status': 'error', 'message': 'Missing club_id'})

    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB connection failed'})

    cursor = conn.cursor(dictionary=True)
    try:
        sql = """SELECT u.Student_ID, u.Username, m.Join_Date
                 FROM membership m
                 JOIN user u ON m.Student_ID = u.Student_ID
                 WHERE m.Club_ID = %s"""
        cursor.execute(sql, (club_id,))
        members = cursor.fetchall()

        # Convert datetime for JSON serialization
        for m in members:
            for key, val in m.items():
                if hasattr(val, 'isoformat'):
                    m[key] = val.isoformat()

        return jsonify({'status': 'success', 'data': members})
    finally:
        cursor.close()
        conn.close()


@clubs_bp.route('/roles', methods=['GET'])
def get_roles():
    """จัดการสิทธิ์ Admin — ดูรายการ Admin / ลบสิทธิ์ Admin"""
    if session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized access'})

    # ส่วนของการลบสิทธิ์ (ปรับเป็น user)
    remove_id = request.args.get('remove_id')
    if remove_id:
        # ห้ามตัวเองลบสิทธิ์ตัวเอง
        if remove_id == session.get('student_id'):
            return jsonify({'status': 'error', 'message': 'ไม่สามารถลบสิทธิ์ตัวเองได้'})

        conn = get_db_connection()
        if not conn:
            return jsonify({'status': 'error', 'message': 'DB connection failed'})

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE user SET Role = 'user' WHERE Student_ID = %s", (remove_id,))
            conn.commit()
            return jsonify({'status': 'success', 'message': 'ปรับสิทธิ์เรียบร้อยแล้ว'})
        except Exception as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': f'เกิดข้อผิดพลาด: {e}'})
        finally:
            cursor.close()
            conn.close()

    # ส่วนของการแสดงข้อมูล Admin
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB connection failed'})

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT Student_ID, Username, Role FROM user WHERE Role = 'admin'")
        roles = cursor.fetchall()
        return jsonify({'status': 'success', 'data': roles})
    finally:
        cursor.close()
        conn.close()


@clubs_bp.route('/issue_certs', methods=['POST'])
def issue_certs():
    """ออกใบรับรองให้สมาชิก (Admin เท่านั้น)"""
    if session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized access'})

    data = request.get_json()
    if not data or 'club_id' not in data or 'student_ids' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid data provided'})

    club_id = data['club_id']
    student_ids = data['student_ids']

    if not isinstance(student_ids, list):
        return jsonify({'status': 'error', 'message': 'Invalid data provided'})

    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB connection failed'})

    cursor = conn.cursor(dictionary=True)
    success_count = 0

    try:
        for sid in student_ids:
            # สร้างรหัส Cert แบบสุ่ม
            raw = hashlib.md5(f"{sid}{time.time()}".encode()).hexdigest()[:8].upper()
            cert_code = f"CERT-{time.strftime('%Y')}-{raw}"

            # ตรวจสอบว่าเคยออกให้หรือยัง
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
        return jsonify({
            'status': 'success',
            'message': f'ออกใบรับรองสำเร็จ {success_count} รายการ',
            'count': success_count
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        cursor.close()
        conn.close()
