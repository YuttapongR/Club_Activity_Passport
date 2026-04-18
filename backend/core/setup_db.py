"""
Utility script สำหรับ setup database tables
รวม logic จาก alter_db.php, check_db.php, setup_cert_tables.php
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.database import get_db_connection


def check_db():
    """ตรวจสอบโครงสร้างตาราง user"""
    conn = get_db_connection()
    if not conn:
        print("Cannot connect to database")
        return

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("DESCRIBE user")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    finally:
        cursor.close()
        conn.close()


def alter_db():
    """เพิ่มคอลัมน์ Role ในตาราง user"""
    conn = get_db_connection()
    if not conn:
        print("Cannot connect to database")
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            "ALTER TABLE user ADD COLUMN Role ENUM('user', 'admin') DEFAULT 'user' NOT NULL"
        )
        conn.commit()
        print("Column Role added.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()


def setup_cert_tables():
    """สร้างตาราง membership และ certificates"""
    conn = get_db_connection()
    if not conn:
        print("Cannot connect to database")
        return

    cursor = conn.cursor()
    try:
        # 1. สร้างตาราง membership
        sql1 = """CREATE TABLE IF NOT EXISTS membership (
            Member_ID INT AUTO_INCREMENT PRIMARY KEY,
            Student_ID VARCHAR(20) NOT NULL,
            Club_ID INT NOT NULL,
            Join_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY (Student_ID, Club_ID)
        )"""
        cursor.execute(sql1)
        print("Table 'membership' created or already exists.")

        # 2. สร้างตาราง certificates
        sql2 = """CREATE TABLE IF NOT EXISTS certificates (
            Cert_ID INT AUTO_INCREMENT PRIMARY KEY,
            Student_ID VARCHAR(20) NOT NULL,
            Club_ID INT NOT NULL,
            Issue_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Cert_Code VARCHAR(50) UNIQUE NOT NULL
        )"""
        cursor.execute(sql2)
        print("Table 'certificates' created or already exists.")

        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Database setup utilities')
    parser.add_argument('action', choices=['check', 'alter', 'setup_certs', 'all'],
                        help='Action to perform')
    args = parser.parse_args()

    if args.action == 'check':
        check_db()
    elif args.action == 'alter':
        alter_db()
    elif args.action == 'setup_certs':
        setup_cert_tables()
    elif args.action == 'all':
        alter_db()
        setup_cert_tables()
        check_db()
