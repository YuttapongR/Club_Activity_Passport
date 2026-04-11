USE club_system;

-- 1. Create activities table
CREATE TABLE IF NOT EXISTS activities (
    Activity_ID INT AUTO_INCREMENT PRIMARY KEY,
    Club_ID INT NOT NULL,
    Activity_Name VARCHAR(150) NOT NULL,
    Description TEXT,
    Activity_Date DATETIME NOT NULL,
    Hours_Given DECIMAL(5,2) DEFAULT 0.00,
    Checkin_Code VARCHAR(20) UNIQUE,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create activity_checkins table
CREATE TABLE IF NOT EXISTS activity_checkins (
    Checkin_ID INT AUTO_INCREMENT PRIMARY KEY,
    Activity_ID INT NOT NULL,
    Student_ID VARCHAR(20) NOT NULL,
    Checkin_Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (Activity_ID, Student_ID)
);
