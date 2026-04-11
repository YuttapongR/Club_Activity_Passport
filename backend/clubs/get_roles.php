<?php
header('Content-Type: application/json');
include '../core/connect_db.php';
session_start();

// ตรวจสอบสิทธิ์ Admin เบื้องต้น
if (!isset($_SESSION['role']) || $_SESSION['role'] !== 'admin') {
    echo json_encode(['status' => 'error', 'message' => 'Unauthorized access']);
    exit();
}

// ส่วนของการลบสิทธิ์ (ปรับเป็น user)
if (isset($_GET['remove_id'])) {
    $student_id = mysqli_real_escape_string($conn, $_GET['remove_id']);

    // ห้ามตัวเองลบสิทธิ์ตัวเอง (เพื่อกันพลาด)
    if ($student_id === $_SESSION['student_id']) {
        echo json_encode(['status' => 'error', 'message' => 'ไม่สามารถลบสิทธิ์ตัวเองได้']);
        exit();
    }

    $sql_update = "UPDATE user SET Role = 'user' WHERE Student_ID = '$student_id'";
    if (mysqli_query($conn, $sql_update)) {
        echo json_encode(['status' => 'success', 'message' => 'ปรับสิทธิ์เรียบร้อยแล้ว']);
    } else {
        echo json_encode(['status' => 'error', 'message' => 'เกิดข้อผิดพลาด: ' . mysqli_error($conn)]);
    }
    exit();
}

// ส่วนของการแสดงข้อมูล (แสดงเฉพาะ Admin เพื่อจัดการสิทธิ์)
$sql = "SELECT Student_ID, Username, Role FROM user WHERE Role = 'admin'";
$result = mysqli_query($conn, $sql);

$role = [];

if ($result) {
    while ($row = mysqli_fetch_array($result)) {
        $role[] = $row;
    }
}

echo json_encode(['status' => 'success', 'data' => $role]);

?>