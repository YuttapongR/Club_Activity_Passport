<?php
session_start();
include "../core/connect_db.php";
header('Content-Type: application/json');

if (!isset($_SESSION['student_id'])) {
    echo json_encode(['status' => 'error', 'message' => 'กรุณาเข้าสู่ระบบ']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
$student_id = $_SESSION['student_id'];

if (isset($input['code'])) {
    $code = mysqli_real_escape_string($conn, $input['code']);

    // 1. Find activity by code
    $activity_sql = "SELECT * FROM activities WHERE Checkin_Code = '$code'";
    $activity_result = mysqli_query($conn, $activity_sql);

    if ($activity_result && mysqli_num_rows($activity_result) > 0) {
        $activity = mysqli_fetch_assoc($activity_result);
        $activity_id = $activity['Activity_ID'];
        $hours = $activity['Hours_Given'];

        // 2. Check if already checked in
        $check_checkin = "SELECT * FROM activity_checkins WHERE Activity_ID = '$activity_id' AND Student_ID = '$student_id'";
        $checkin_result = mysqli_query($conn, $check_checkin);

        if (mysqli_num_rows($checkin_result) > 0) {
            echo json_encode(['status' => 'error', 'message' => 'คุณได้บันทึกเวลาเข้าร่วมกิจกรรมนี้ไปแล้ว']);
            exit;
        }

        // 3. Start Transaction
        mysqli_begin_transaction($conn);
        try {
            // Record check-in
            $sql_in = "INSERT INTO activity_checkins (Activity_ID, Student_ID) VALUES ('$activity_id', '$student_id')";
            mysqli_query($conn, $sql_in);

            // Update user's total hours
            $sql_user = "UPDATE user SET Total_Hours = IFNULL(Total_Hours, 0) + $hours WHERE Student_ID = '$student_id'";
            mysqli_query($conn, $sql_user);

            mysqli_commit($conn);
            echo json_encode(['status' => 'success', 'message' => 'บันทึกเวลาสำเร็จ! คุณได้รับ ' . $hours . ' ชั่วโมง']);
        } catch (Exception $e) {
            mysqli_rollback($conn);
            echo json_encode(['status' => 'error', 'message' => 'เกิดข้อผิดพลาดในการบันทึกข้อมูล']);
        }
    } else {
        echo json_encode(['status' => 'error', 'message' => 'รหัสกิจกรรมไม่ถูกต้อง']);
    }
} else {
    echo json_encode(['status' => 'error', 'message' => 'กรุณาระบุรหัสกิจกรรม']);
}
?>
