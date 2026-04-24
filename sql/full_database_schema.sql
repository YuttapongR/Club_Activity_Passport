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
    Role ENUM('user', 'admin') DEFAULT 'user' NOT NULL
);

-- 2. ตาราง club
CREATE TABLE IF NOT EXISTS club (
    Club_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name_Club VARCHAR(150) NOT NULL,
    Description TEXT,
    Club_type VARCHAR(100),
    Member VARCHAR(50),
    Club_Image VARCHAR(255)
);

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

-- 4. ตาราง certificates
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
