USE club_system;

-- 1. ตาราง user
CREATE TABLE IF NOT EXISTS user (
    Student_ID VARCHAR(255) PRIMARY KEY,
    Username VARCHAR(100) UNIQUE NOT NULL,
    First_Name VARCHAR(100),
    Last_Name VARCHAR(100),
    Password VARCHAR(255) NOT NULL,
    Phone VARCHAR(20),
    Email VARCHAR(100),
    Role ENUM('user', 'admin') DEFAULT 'user' NOT NULL,
    Total_Hours DECIMAL(5,2) DEFAULT 0.00
) ENGINE=InnoDB;

-- 2. ตาราง club
CREATE TABLE IF NOT EXISTS club (
    Club_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name_Club VARCHAR(150) NOT NULL,
    Description TEXT,
    Club_type VARCHAR(100),
    Member VARCHAR(50),
    Club_Image VARCHAR(255)
) ENGINE=InnoDB;

-- 3. ตาราง membership
CREATE TABLE IF NOT EXISTS membership (
    Member_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID VARCHAR(255) NOT NULL,
    Club_ID INT NOT NULL,
    Join_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (Student_ID, Club_ID),
    CONSTRAINT fk_mem_student FOREIGN KEY (Student_ID) REFERENCES user(Student_ID) ON DELETE CASCADE,
    CONSTRAINT fk_mem_club FOREIGN KEY (Club_ID) REFERENCES club(Club_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. ตาราง activities
CREATE TABLE IF NOT EXISTS activities (
    Activity_ID INT AUTO_INCREMENT PRIMARY KEY,
    Club_ID INT NOT NULL,
    Activity_Name VARCHAR(150) NOT NULL,
    Description TEXT,
    Activity_Date DATETIME NOT NULL,
    Hours_Given DECIMAL(5,2) DEFAULT 0.00,
    Checkin_Code VARCHAR(20) UNIQUE,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_act_club FOREIGN KEY (Club_ID) REFERENCES club(Club_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. ตาราง activity_registrations (ลงชื่อเข้าร่วมกิจกรรม)
CREATE TABLE IF NOT EXISTS activity_registrations (
    Registration_ID INT AUTO_INCREMENT PRIMARY KEY,
    Activity_ID INT NOT NULL,
    Student_ID VARCHAR(255) NOT NULL,
    Registration_Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (Activity_ID, Student_ID),
    CONSTRAINT fk_reg_activity FOREIGN KEY (Activity_ID) REFERENCES activities(Activity_ID) ON DELETE CASCADE,
    CONSTRAINT fk_reg_student FOREIGN KEY (Student_ID) REFERENCES user(Student_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. ตาราง activity_checkins (เช็คอินรับชั่วโมง)
CREATE TABLE IF NOT EXISTS activity_checkins (
    Checkin_ID INT AUTO_INCREMENT PRIMARY KEY,
    Activity_ID INT NOT NULL,
    Student_ID VARCHAR(255) NOT NULL,
    Checkin_Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (Activity_ID, Student_ID),
    CONSTRAINT fk_check_activity FOREIGN KEY (Activity_ID) REFERENCES activities(Activity_ID) ON DELETE CASCADE,
    CONSTRAINT fk_check_student FOREIGN KEY (Student_ID) REFERENCES user(Student_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. ตาราง certificates
CREATE TABLE IF NOT EXISTS certificates (
    Cert_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID VARCHAR(255) NOT NULL,
    Club_ID INT NOT NULL,
    Issue_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Cert_Code VARCHAR(50) UNIQUE NOT NULL,
    CONSTRAINT fk_cert_student FOREIGN KEY (Student_ID) REFERENCES user(Student_ID) ON DELETE CASCADE,
    CONSTRAINT fk_cert_club FOREIGN KEY (Club_ID) REFERENCES club(Club_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- เพิ่ม Admin ตัวอย่าง (ถ้ายังไม่มี)
INSERT IGNORE INTO user (Student_ID, Username, First_Name, Last_Name, Password, Role) 
VALUES ('ADMIN001', 'admin', 'System', 'Admin', '123456', 'admin');
