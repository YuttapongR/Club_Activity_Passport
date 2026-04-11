<?php
header('Content-Type: application/json');
include '../core/connect_db.php';
session_start();

if (isset($_GET['club_id'])) {
    $club_id = mysqli_real_escape_string($conn, $_GET['club_id']);
    $student_id = isset($_SESSION['student_id']) ? $_SESSION['student_id'] : null;

    // 1. ดึงข้อมูลชมรม
    $sql = "SELECT * FROM club WHERE Club_ID = '$club_id'";
    $result = mysqli_query($conn, $sql);

    if ($result && mysqli_num_rows($result) > 0) {
        $club = mysqli_fetch_assoc($result);

        // 2. ตรวจสอบสถานะการเป็นสมาชิก
        $is_member = false;
        $current_members = 0;

        try {
            if ($student_id) {
                $member_sql = "SELECT Member_ID FROM membership WHERE Student_ID = '$student_id' AND Club_ID = '$club_id'";
                $member_result = mysqli_query($conn, $member_sql);
                if ($member_result && mysqli_num_rows($member_result) > 0) {
                    $is_member = true;
                }
            }

            // 3. ดึงจำนวนสมาชิกปัจจุบัน
            $count_sql = "SELECT COUNT(*) as total FROM membership WHERE Club_ID = '$club_id'";
            $count_result = mysqli_query($conn, $count_sql);
            if ($count_result) {
                $count_row = mysqli_fetch_assoc($count_result);
                $current_members = $count_row['total'];
            }
        } catch (Exception $e) {
            // หากตาราง membership ยังไม่มี ให้ข้ามส่วนนี้ไปก่อน
        }

        echo json_encode([
            'status' => 'success',
            'data' => $club,
            'is_member' => $is_member,
            'current_members' => $current_members
        ]);
    } else {
        echo json_encode(['status' => 'error', 'message' => 'ไม่พบข้อมูลชมรม']);
    }
} else {
    echo json_encode(['status' => 'error', 'message' => 'Missing club_id']);
}
?>