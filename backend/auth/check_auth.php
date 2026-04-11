<?php
session_start();
header('Content-Type: application/json');

if (isset($_SESSION['student_id'])) {
    echo json_encode([
        'status' => 'success',
        'role' => isset($_SESSION['role']) ? $_SESSION['role'] : 'user',
        'username' => $_SESSION['username']
    ]);
} else {
    echo json_encode(['status' => 'error', 'message' => 'Not logged in']);
}
?>