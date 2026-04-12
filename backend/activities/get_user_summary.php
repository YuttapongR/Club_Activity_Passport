<?php
session_start();
include "../core/connect_db.php";
header('Content-Type: application/json');

if (!isset($_SESSION['student_id'])) {
    echo json_encode(['status' => 'error', 'message' => 'Not logged in']);
    exit;
}

$student_id = $_SESSION['student_id'];

// 1. Get user total hours
$user_sql = "SELECT Total_Hours FROM user WHERE Student_ID = '$student_id'";
$user_result = mysqli_query($conn, $user_sql);
$user_data = mysqli_fetch_assoc($user_result);
$total_hours = $user_data['Total_Hours'] ?? 0;

// 2. Get activities user checked into
$activities_sql = "SELECT a.Activity_Name, a.Hours_Given, c.Checkin_Time, cl.Name_Club
                   FROM activity_checkins c
                   JOIN activities a ON c.Activity_ID = a.Activity_ID
                   LEFT JOIN club cl ON a.Club_ID = cl.Club_ID
                   WHERE c.Student_ID = '$student_id'
                   ORDER BY c.Checkin_Time DESC";

$activities_result = mysqli_query($conn, $activities_sql);
$history = [];

if ($activities_result) {
    while ($row = mysqli_fetch_assoc($activities_result)) {
        $history[] = $row;
    }
}

echo json_encode([
    'status' => 'success',
    'total_hours' => $total_hours,
    'history' => $history
]);
?>