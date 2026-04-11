<?php
include "connect_db.php";

// 1. สร้างตาราง membership
$sql1 = "CREATE TABLE IF NOT EXISTS membership (
    Member_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID VARCHAR(20) NOT NULL,
    Club_ID INT NOT NULL,
    Join_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (Student_ID, Club_ID)
)";

// 2. สร้างตาราง certificates
$sql2 = "CREATE TABLE IF NOT EXISTS certificates (
    Cert_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID VARCHAR(20) NOT NULL,
    Club_ID INT NOT NULL,
    Issue_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Cert_Code VARCHAR(50) UNIQUE NOT NULL
)";

if (mysqli_query($conn, $sql1)) {
    echo "Table 'membership' created or already exists.<br>";
} else {
    echo "Error creating table 'membership': " . mysqli_error($conn) . "<br>";
}

if (mysqli_query($conn, $sql2)) {
    echo "Table 'certificates' created or already exists.<br>";
} else {
    echo "Error creating table 'certificates': " . mysqli_error($conn) . "<br>";
}
?>