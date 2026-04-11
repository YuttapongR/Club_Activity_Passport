<?php
header('Content-Type: application/json');
include '../core/connect_db.php';
session_start();

// ตรวจสอบสิทธิ์ Admin
if (!isset($_SESSION['role']) || $_SESSION['role'] !== 'admin') {
    echo json_encode(['status' => 'error', 'message' => 'Unauthorized access']);
    exit();
}

$input = json_decode(file_get_contents('php://input'), true);

if (isset($input['club_id']) && isset($input['student_ids']) && is_array($input['student_ids'])) {
    $club_id = mysqli_real_escape_string($conn, $input['club_id']);
    $student_ids = $input['student_ids'];
    $success_count = 0;

    foreach ($student_ids as $sid) {
        $sid = mysqli_real_escape_string($conn, $sid);

        // สร้างรหัส Cert แบบสุ่ม (จำลอง)
        $cert_code = "CERT-" . date("Y") . "-" . strtoupper(substr(md5($sid . time()), 0, 8));

        // ตรวจสอบว่าเคยออกให้หรือยัง (เพื่อไม่ให้ซ้ำ)
        $check_sql = "SELECT Cert_ID FROM certificates WHERE Student_ID = '$sid' AND Club_ID = '$club_id'";
        $check_result = mysqli_query($conn, $check_sql);

        if (mysqli_num_rows($check_result) == 0) {
            $sql = "INSERT INTO certificates (Student_ID, Club_ID, Cert_Code) VALUES ('$sid', '$club_id', '$cert_code')";
            if (mysqli_query($conn, $sql)) {
                $success_count++;
            }
        }
    }

    echo json_encode([
        'status' => 'success',
        'message' => "ออกใบรับรองสำเร็จ $success_count รายการ",
        'count' => $success_count
    ]);
} else {
    echo json_encode(['status' => 'error', 'message' => 'Invalid data provided']);
}
?>