<?php
session_start();
include "../core/connect_db.php";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // ป้องกัน SQL Injection เบื้องต้น
    $username = mysqli_real_escape_string($conn, $username);
    $password = mysqli_real_escape_string($conn, $password);

    // ตรวจสอบว่ามีผู้ใช้นี้ในระบบหรือไม่ (ล็อกอินได้ทั้ง Username และ Student_ID)
    $sql = "SELECT * FROM user WHERE (Username = '$username' OR Student_ID = '$username') AND Password = '$password'";
    $result = mysqli_query($conn, $sql);

    if (mysqli_num_rows($result) === 1) {
        // ล็อกอินสำเร็จ เก็บข้อมูลลง Session
        $row = mysqli_fetch_assoc($result);
        $_SESSION['student_id'] = $row['Student_ID'];
        $_SESSION['username'] = $row['Username'];
        $_SESSION['firstname'] = $row['First_Name'];
        $_SESSION['lastname'] = $row['Last_Name'];
        $_SESSION['role'] = $row['Role']; // เก็บ Role ลงใน session ด้วย

        echo "<script>
            alert('เข้าสู่ระบบสำเร็จ');
            window.location.href = '../../frontend/dashboard/main.html';
        </script>";
    } else {
        // ล็อกอินไม่สำเร็จ
        echo "<script>
            alert('ชื่อผู้ใช้งาน หรือ รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง');
            window.history.back();
        </script>";
    }
}
?>