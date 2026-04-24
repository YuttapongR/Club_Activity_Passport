import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import get_db_connection

def apply_schema():
    conn = get_db_connection()
    if not conn:
        print("Cannot connect to database")
        return

    cursor = conn.cursor()
    try:
        # Add Total_Hours if not exists
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN Total_Hours DECIMAL(5,2) DEFAULT 0.00;")
            print("Added Total_Hours to user table.")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("Column Total_Hours already exists.")
            else:
                print(f"Error adding Total_Hours: {e}")

        # Create activity_registrations
        sql = """
        CREATE TABLE IF NOT EXISTS activity_registrations (
            Registration_ID INT AUTO_INCREMENT PRIMARY KEY,
            Activity_ID INT NOT NULL,
            Student_ID VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
            Registration_Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY (Activity_ID, Student_ID),
            CONSTRAINT fk_reg_activity FOREIGN KEY (Activity_ID) REFERENCES activities(Activity_ID) ON DELETE CASCADE,
            CONSTRAINT fk_reg_student FOREIGN KEY (Student_ID) REFERENCES user(Student_ID) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """
        cursor.execute(sql)
        print("Created activity_registrations table.")
        
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    apply_schema()
