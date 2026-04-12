<?php
session_start();
include "../core/connect_db.php";
header('Content-Type: application/json');

// Check admin role
if (!isset($_SESSION['role']) || $_SESSION['role'] !== 'admin') {
    echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);

if (isset($input['activity_name'], $input['activity_date'], $input['hours'])) {
    // Check if club_id is set and not null, otherwise default to 0 for global activities
    $club_id_val = isset($input['club_id']) && $input['club_id'] !== null ? $input['club_id'] : 0;
    $club_id = "'" . mysqli_real_escape_string($conn, $club_id_val) . "'";
    $name = mysqli_real_escape_string($conn, $input['activity_name']);
    $desc = mysqli_real_escape_string($conn, $input['description'] ?? '');
    $date = mysqli_real_escape_string($conn, $input['activity_date']);
    $hours = mysqli_real_escape_string($conn, $input['hours']);

    // Generate unique 6-digit checkin code
    $checkin_code = strtoupper(substr(md5(uniqid(mt_rand(), true)), 0, 6));

    $sql = "INSERT INTO activities (Club_ID, Activity_Name, Description, Activity_Date, Hours_Given, Checkin_Code) 
            VALUES ($club_id, '$name', '$desc', '$date', '$hours', '$checkin_code')";

    if (mysqli_query($conn, $sql)) {
        echo json_encode(['status' => 'success', 'message' => 'เพิ่มกิจกรรมสำเร็จ', 'code' => $checkin_code]);
    } else {
        echo json_encode(['status' => 'error', 'message' => mysqli_error($conn)]);
    }
} else {
    echo json_encode(['status' => 'error', 'message' => 'ข้อมูลไม่ครบถ้วน']);
}
?>