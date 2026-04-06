<?php
header('Content-Type: application/json');
include '../core/connect_db.php';

$sql = "SELECT * FROM club ORDER BY Club_ID DESC";
$result = mysqli_query($conn, $sql);

$clubs = [];
if ($result) {
    while ($row = mysqli_fetch_assoc($result)) {
        $clubs[] = $row;
    }
}

echo json_encode(['status' => 'success', 'data' => $clubs]);
?>