<?php
session_start();
header('Content-Type: application/json');
include '../core/connect_db.php';

// ตรวจสอบว่าล็อกอินอยู่หรือไม่
if (!isset($_SESSION['student_id'])) {
    echo json_encode(['status' => 'error', 'message' => 'กรุณาล็อกอินก่อนเข้าร่วมชมรม']);
    exit();
}

if (isset($_GET['club_id'])) {
    $student_id = $_SESSION['student_id'];
    $club_id = mysqli_real_escape_string($conn, $_GET['club_id']);

    // ตรวจสอบว่าเคยเข้าหรือยัง
    $check_sql = "SELECT Member_ID FROM membership WHERE Student_ID = '$student_id' AND Club_ID = '$club_id'";
    $check_result = mysqli_query($conn, $check_sql);

    if (mysqli_num_rows($check_result) > 0) {
        // ถ้าเคยเข้าแล้ว ให้เด้งกลับไปหน้าเดิม (หรือแสดงข้อความ)
        echo "<script>alert('คุณเป็นสมาชิกชมรมนี้อยู่แล้ว'); window.location.href = '../../frontend/dashboard/main.html';</script>";
        exit();
    }

    $sql = "INSERT INTO membership (Student_ID, Club_ID) VALUES ('$student_id', '$club_id')";
    if (mysqli_query($conn, $sql)) {
        echo "<script>alert('เข้าร่วมชมรมสำเร็จ!'); window.location.href = '../../frontend/dashboard/main.html';</script>";
    } else {
        echo "<script>alert('เกิดข้อผิดพลาดในการเข้าร่วมชมรม'); window.location.href = '../../frontend/dashboard/main.html';</script>";
    }
} else {
    echo "Invalid request";
}
?>