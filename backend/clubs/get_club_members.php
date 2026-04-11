<?php
header('Content-Type: application/json');
include '../core/connect_db.php';
session_start();

// ตรวจสอบสิทธิ์ Admin
if (!isset($_SESSION['role']) || $_SESSION['role'] !== 'admin') {
    echo json_encode(['status' => 'error', 'message' => 'Unauthorized access']);
    exit();
}

if (isset($_GET['club_id'])) {
    $club_id = mysqli_real_escape_string($conn, $_GET['club_id']);

    // ดึงรายชื่อสมาชิกโดย Join กับตาราง user เพื่อเอาชื่อมาโชว์
    $sql = "SELECT u.Student_ID, u.Username, m.Join_Date 
            FROM membership m
            JOIN user u ON m.Student_ID = u.Student_ID
            WHERE m.Club_ID = '$club_id'";

    $result = mysqli_query($conn, $sql);
    $members = [];

    if ($result) {
        while ($row = mysqli_fetch_assoc($result)) {
            $members[] = $row;
        }
    }

    echo json_encode(['status' => 'success', 'data' => $members]);
} else {
    echo json_encode(['status' => 'error', 'message' => 'Missing club_id']);
}
?>