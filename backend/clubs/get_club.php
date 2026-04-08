<?php
header('Content-Type: application/json');

if (isset($_GET['id'])) {
    $club_id = mysqli_real_escape_string($conn, $_GET['id']);

    // ดึงข้อมูลเพื่อลบรูปภาพ (ถ้ามี)
    $sql_img = "SELECT Club_image FROM club WHERE Club_ID = '$club_id'";
    $res_img = mysqli_query($conn, $sql_img);
    if ($row = mysqli_fetch_assoc($res_img)) {
        $img_path = "../../uploads/" . $row['Club_image'];
        if (file_exists($img_path) && !empty($row['Club_image'])) {
            unlink($img_path); // ลบไฟล์รูปภาพ
        }
    }

    $sql = "DELETE FROM club WHERE Club_ID = '$club_id'";
    if (mysqli_query($conn, $sql)) {
        echo "<script>alert('ลบชมรมสำเร็จ'); window.history.back();</script>";
    } else {
        echo "<script>alert('ลบชมรมไม่สำเร็จ'); window.history.back();</script>";
    }
} else {
    echo "Invalid request";
}
?>