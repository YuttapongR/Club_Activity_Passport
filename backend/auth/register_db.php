<?php
include "../core/connect_db.php";
if (isset($_REQUEST['bt'])) {
    $student_id = $_REQUEST['student_id'];
    $username = $_REQUEST['username'];
    $firstname = $_REQUEST['firstname'];
    $lastname = $_REQUEST['lastname'];
    $password = $_REQUEST['password'];
    $confirm_password = $_REQUEST['confirm_password'];
    $phone = $_REQUEST['phone'];
    $email = $_REQUEST['email'];

    if ($password != $confirm_password) {
        echo "<script>alert('รหัสผ่านไม่ตรงกัน'); window.history.back();</script>";
    } else {
        $sql = "INSERT INTO user (Student_ID, Username, First_Name , Last_Name, Password, Phone, Email) 
        VALUES ('$student_id', '$username', '$firstname', '$lastname', '$password', '$phone', '$email')";
        $result = mysqli_query($conn, $sql);
        if ($result) {
            echo "<script>alert('สมัครสมาชิกสำเร็จ'); window.location.href='../../frontend/auth/login.html';</script>";
        } else {
            echo "<script>alert('สมัครสมาชิกไม่สำเร็จ'); window.history.back();</script>";
        }
    }
}
?>