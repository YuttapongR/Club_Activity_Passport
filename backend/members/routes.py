from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from backend.core.database import get_db_connection

router = APIRouter()


@router.get("/join", response_class=HTMLResponse)
def join_club(request: Request, club_id: str = None):
    """เข้าร่วมชมรม"""
    # ตรวจสอบว่าล็อกอินหรือยัง
    if 'student_id' not in request.session:
        return HTMLResponse("""<script>
            alert('กรุณาเข้าสู่ระบบก่อนเข้าร่วมชมรม');
            window.location.href = '/frontend/auth/login.html';
        </script>""")

    student_id = request.session['student_id']

    if not club_id:
        return HTMLResponse("""<script>
            alert('ไม่พบรหัสชมรม');
            window.history.back();
        </script>""")

    conn = get_db_connection()
    if not conn:
        return HTMLResponse("<script>alert('ไม่สามารถเชื่อมต่อฐานข้อมูลได้'); window.history.back();</script>")

    cursor = conn.cursor(dictionary=True)
    try:
        # ตรวจสอบว่าสมัครไปหรือยัง
        cursor.execute(
            "SELECT * FROM membership WHERE Student_ID = %s AND Club_ID = %s",
            (student_id, club_id)
        )
        if cursor.fetchone():
            return HTMLResponse("""<script>
                alert('คุณเป็นสมาชิกชมรมนี้อยู่แล้ว');
                window.history.back();
            </script>""")

        # ตรวจสอบจำนวนสมาชิก (ถ้ามีการจำกัด)
        cursor.execute("SELECT Member FROM club WHERE Club_ID = %s", (club_id,))
        club_data = cursor.fetchone()

        if club_data and club_data['Member'] != 'ไม่จำกัด':
            cursor.execute("SELECT COUNT(*) as total FROM membership WHERE Club_ID = %s", (club_id,))
            count_data = cursor.fetchone()
            try:
                max_members = int(club_data['Member'])
                if count_data and count_data['total'] >= max_members:
                    return HTMLResponse("""<script>
                        alert('ขออภัย ชมรมนี้มีสมาชิกเต็มแล้ว');
                        window.history.back();
                    </script>""")
            except (ValueError, TypeError):
                pass

        # ทำการเพิ่มสมาชิกลงในตาราง membership
        cursor.execute(
            "INSERT INTO membership (Student_ID, Club_ID) VALUES (%s, %s)",
            (student_id, club_id)
        )
        conn.commit()
        return HTMLResponse(f"""<script>
            alert('ดำเนินการเข้าร่วมชมรมสำเร็จ');
            window.location.href = '/frontend/dashboard/club_detail.html?id={club_id}';
        </script>""")
    except Exception as e:
        conn.rollback()
        error_msg = str(e).replace("'", "\\'")
        return HTMLResponse(f"""<script>
            alert('เกิดข้อผิดพลาด: {error_msg}');
            window.history.back();
        </script>""")
    finally:
        cursor.close()
        conn.close()


@router.get("/search")
def search_club(q: str = ""):
    """ค้นหาชมรมจากชื่อหรือรายละเอียด"""
    conn = get_db_connection()
    if not conn:
        return {'status': 'error', 'message': 'DB connection failed'}

    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM club WHERE Name_Club LIKE %s OR Description LIKE %s"
        search_term = f"%{q}%"
        cursor.execute(sql, (search_term, search_term))
        clubs = cursor.fetchall()
        return {'status': 'success', 'data': clubs, 'count': len(clubs)}
    finally:
        cursor.close()
        conn.close()
