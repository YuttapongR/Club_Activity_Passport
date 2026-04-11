<?php
session_start();
include "../core/connect_db.php";
header('Content-Type: application/json');

if (!isset($_SESSION['role']) || $_SESSION['role'] !== 'admin') {
    echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);

if (isset($input['activity_id'])) {
    $id = mysqli_real_escape_string($conn, $input['activity_id']);

    // Delete checkins first due to FK constraints (or just delete them)
    mysqli_query($conn, "DELETE FROM activity_checkins WHERE Activity_ID = '$id'");
    
    $sql = "DELETE FROM activities WHERE Activity_ID = '$id'";

    if (mysqli_query($conn, $sql)) {
        echo json_encode(['status' => 'success', 'message' => 'ลบกิจกรรมเรียบร้อยแล้ว']);
    } else {
        echo json_encode(['status' => 'error', 'message' => mysqli_error($conn)]);
    }
} else {
    echo json_encode(['status' => 'error', 'message' => 'Missing activity_id']);
}
?>
