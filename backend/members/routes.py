from flask import Blueprint, request, session, jsonify

from backend.core.database import get_db_connection

members_bp = Blueprint('members', __name__)


@members_bp.route('/join', methods=['GET'])
def join_club():
    """เข้าร่วมชมรม"""
    # ตรวจสอบว่าล็อกอินหรือยัง
    if 'student_id' not in session:
        return """<script>
            alert('กรุณาเข้าสู่ระบบก่อนเข้าร่วมชมรม');
            window.location.href = '/frontend/auth/login.html';
        </script>"""

    student_id = session['student_id']
    club_id = request.args.get('club_id')

    if not club_id:
        return """<script>
            alert('ไม่พบรหัสชมรม');
            window.history.back();
        </script>"""

    conn = get_db_connection()
    if not conn:
        return "<script>alert('ไม่สามารถเชื่อมต่อฐานข้อมูลได้'); window.history.back();</script>"

    cursor = conn.cursor(dictionary=True)
    try:
        # ตรวจสอบว่าสมัครไปหรือยัง
        cursor.execute(
            "SELECT * FROM membership WHERE Student_ID = %s AND Club_ID = %s",
            (student_id, club_id)
        )
        if cursor.fetchone():
            return """<script>
                alert('คุณเป็นสมาชิกชมรมนี้อยู่แล้ว');
                window.history.back();
            </script>"""

        # ตรวจสอบจำนวนสมาชิก (ถ้ามีการจำกัด)
        cursor.execute("SELECT Member FROM club WHERE Club_ID = %s", (club_id,))
        club_data = cursor.fetchone()

        if club_data and club_data['Member'] != 'ไม่จำกัด':
            cursor.execute("SELECT COUNT(*) as total FROM membership WHERE Club_ID = %s", (club_id,))
            count_data = cursor.fetchone()
            try:
                max_members = int(club_data['Member'])
                if count_data and count_data['total'] >= max_members:
                    return """<script>
                        alert('ขออภัย ชมรมนี้มีสมาชิกเต็มแล้ว');
                        window.history.back();
                    </script>"""
            except (ValueError, TypeError):
                pass

        # ทำการเพิ่มสมาชิกลงในตาราง membership
        cursor.execute(
            "INSERT INTO membership (Student_ID, Club_ID) VALUES (%s, %s)",
            (student_id, club_id)
        )
        conn.commit()
        return f"""<script>
            alert('ดำเนินการเข้าร่วมชมรมสำเร็จ');
            window.location.href = '/frontend/dashboard/club_detail.html?id={club_id}';
        </script>"""
    except Exception as e:
        conn.rollback()
        error_msg = str(e).replace("'", "\\'")
        return f"""<script>
            alert('เกิดข้อผิดพลาด: {error_msg}');
            window.history.back();
        </script>"""
    finally:
        cursor.close()
        conn.close()


@members_bp.route('/search', methods=['GET'])
def search_club():
    """ค้นหาชมรมจากชื่อหรือรายละเอียด"""
    q = request.args.get('q', '')

    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB connection failed'})

    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM club WHERE Name_Club LIKE %s OR Description LIKE %s"
        search_term = f"%{q}%"
        cursor.execute(sql, (search_term, search_term))
        clubs = cursor.fetchall()
        return jsonify({'status': 'success', 'data': clubs, 'count': len(clubs)})
    finally:
        cursor.close()
        conn.close()
