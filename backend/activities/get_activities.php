<?php
session_start();
include "../core/connect_db.php";
header('Content-Type: application/json');

$club_id = isset($_GET['club_id']) ? mysqli_real_escape_string($conn, $_GET['club_id']) : null;

$sql = "SELECT * FROM activities";
if ($club_id !== null && $club_id !== '') {
    $sql .= " WHERE Club_ID = '$club_id'";
}
$sql .= " ORDER BY Activity_Date DESC";

$result = mysqli_query($conn, $sql);
$activities = [];

if ($result) {
    while ($row = mysqli_fetch_assoc($result)) {
        $activities[] = $row;
    }
    echo json_encode(['status' => 'success', 'data' => $activities]);
} else {
    echo json_encode(['status' => 'error', 'message' => mysqli_error($conn)]);
}
?>