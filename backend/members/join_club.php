<?php
session_start();
header('Content-Type: application/json');
include '../core/connect_db.php';

// ตรวจสอบว่าล็อกอินอยู่หรือไม่
if (!isset($_SESSION['student_id'])) {
    echo json_encode(['status' => 'error', 'message' => 'กรุณาล็อกอินก่อนเข้าร่วมชมรม']);
    exit();
}

?>