<?php
session_start();
include '../core/connect_db.php';

// ตรวจสอบว่าล็อกอินหรือยัง
if (!isset($_SESSION['student_id'])) {
    echo "<script>
        alert('กรุณาเข้าสู่ระบบก่อนเข้าร่วมชมรม');
        window.location.href = '../../frontend/auth/login.html';
    </script>";
    exit();
}

$student_id = $_SESSION['student_id'];
$club_id = isset($_GET['club_id']) ? mysqli_real_escape_string($conn, $_GET['club_id']) : null;

if (!$club_id) {
    echo "<script>
        alert('ไม่พบรหัสชมรม');
        window.history.back();
    </script>";
    exit();
}

// ตรวจสอบว่าสมัครไปหรือยัง
$check_sql = "SELECT * FROM membership WHERE Student_ID = '$student_id' AND Club_ID = '$club_id'";
$check_result = mysqli_query($conn, $check_sql);

if (mysqli_num_rows($check_result) > 0) {
    echo "<script>
        alert('คุณเป็นสมาชิกชมรมนี้อยู่แล้ว');
        window.history.back();
    </script>";
    exit();
}

// ตรวจสอบจำนวนสมาชิก (ถ้ามีการจำกัด)
$club_sql = "SELECT Member FROM club WHERE Club_ID = '$club_id'";
$club_result = mysqli_query($conn, $club_sql);
$club_data = mysqli_fetch_assoc($club_result);

if ($club_data['Member'] !== 'ไม่จำกัด') {
    $count_sql = "SELECT COUNT(*) as total FROM membership WHERE Club_ID = '$club_id'";
    $count_result = mysqli_query($conn, $count_sql);
    $count_data = mysqli_fetch_assoc($count_result);

    if ($count_data['total'] >= (int) $club_data['Member']) {
        echo "<script>
            alert('ขออภัย ชมรมนี้มีสมาชิกเต็มแล้ว');
            window.history.back();
        </script>";
        exit();
    }
}

// ทำการเพิ่มสมาชิกลงในตาราง membership
$insert_sql = "INSERT INTO membership (Student_ID, Club_ID) VALUES ('$student_id', '$club_id')";

if (mysqli_query($conn, $insert_sql)) {
    echo "<script>
        alert('ดำเนินการเข้าร่วมชมรมสำเร็จ');
        window.location.href = '../../frontend/dashboard/club_detail.html?id=$club_id';
    </script>";
} else {
    echo "<script>
        alert('เกิดข้อผิดพลาด: " . mysqli_error($conn) . "');
        window.history.back();
    </script>";
}
?>