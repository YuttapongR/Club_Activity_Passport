import mysql.connector
from mysql.connector import Error
from backend.core.config import DB_CONFIG


def get_db_connection():
    """สร้าง connection ไปยัง MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
