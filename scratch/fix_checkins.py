import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

os.environ['DB_HOST'] = 'localhost'
from backend.core.database import get_db_connection

def fix_checkins_table():
    conn = get_db_connection()
    if not conn:
        print("Cannot connect to database")
        return

    cursor = conn.cursor()
    print("Fixing activity_checkins table...")
    
    try:
        # 1. ปรับขนาดและ Collation ให้ตรงกับตาราง User
        print("Aligning column types...")
        cursor.execute("ALTER TABLE activity_checkins MODIFY Student_ID VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL")

        # 2. ล้างข้อมูลขยะที่ไม่มีในตารางหลัก (ป้องกันการสร้าง FK ไม่ผ่าน)
        print("Cleaning up orphaned checkins...")
        cursor.execute("DELETE FROM activity_checkins WHERE Student_ID NOT IN (SELECT Student_ID FROM user)")
        cursor.execute("DELETE FROM activity_checkins WHERE Activity_ID NOT IN (SELECT Activity_ID FROM activities)")

        # 3. ลบ constraint เก่า (ถ้ามี)
        for fk in ['fk_checkin_student', 'fk_checkin_activity']:
            try:
                cursor.execute(f"ALTER TABLE activity_checkins DROP FOREIGN KEY {fk}")
            except:
                pass

        # 4. เพิ่ม constraint ใหม่พร้อม ON DELETE CASCADE
        print("Adding Foreign Keys with ON DELETE CASCADE...")
        cursor.execute("ALTER TABLE activity_checkins ADD CONSTRAINT fk_checkin_student FOREIGN KEY (Student_ID) REFERENCES user(Student_ID) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE activity_checkins ADD CONSTRAINT fk_checkin_activity FOREIGN KEY (Activity_ID) REFERENCES activities(Activity_ID) ON DELETE CASCADE")
        
        conn.commit()
        print("SUCCESS: activity_checkins table fixed.")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    fix_checkins_table()
