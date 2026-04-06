<?php

include "../core/connect_db.php";

if (isset($_REQUEST['saveclub'])) {
    $nameclub = $_REQUEST['club_name'];
    $desc = $_REQUEST['description'];
    $clubtype = $_REQUEST['category'];
    $member = $_REQUEST['max_members'];

    // ตั้งค่าเบื้องต้นให้เป็นค่าว่างเผื่อไม่ได้อัปโหลดรูป
    $image = "";

    // จัดการการอัปโหลดไฟล์ภาพ
    if (isset($_FILES['club_image']) && $_FILES['club_image']['error'] == 0) {
        $target_dir = "../../uploads/";
        if (!file_exists($target_dir)) {
            mkdir($target_dir, 0777, true);
        }
        $image = basename($_FILES["club_image"]["name"]);
        $target_file = $target_dir . time() . "_" . $image;
        if (move_uploaded_file($_FILES["club_image"]["tmp_name"], $target_file)) {
            $image = time() . "_" . $image; // เปลี่ยนชื่อไฟล์เพื่อไม่ให้ซ้ำในฐานข้อมูล
        }
    }

    $sql = "INSERT INTO club (Name_Club, Description, Club_type, Member, Club_image) VALUES ('$nameclub', '$desc', '$clubtype', '$member', '$image')";
    $result = mysqli_query($conn, $sql);

    if ($result) {
        echo "<script>alert('สร้างชมรมสำเร็จ'); window.location.href= '../../frontend/admin/Admin.html';</script>";
    } else {
        echo "<script>alert('สร้างชมรมไม่สำเร็จ'); window.history.back();</script>";
    }
}

?>