<?php

include "../core/connect_db.php";

if (isset($_REQUEST['saveclub'])) {
    // ป้องกัน SQL Injection โดยการใช้ mysqli_real_escape_string
    $nameclub = mysqli_real_escape_string($conn, $_POST['club_name']);
    $desc = mysqli_real_escape_string($conn, $_POST['description']);
    $clubtype = mysqli_real_escape_string($conn, $_POST['category']);
    $member = !empty($_POST['max_members']) ? mysqli_real_escape_string($conn, $_POST['max_members']) : 'ไม่จำกัด';

    // ตั้งค่าเริ่มต้นของรูปภาพ (ใช้ค่า default_club.png หากไม่มีการอัปโหลดหรืออัปโหลดไม่สำเร็จ)
    $image = "default_club.png";

    // จัดการการอัปโหลดไฟล์ภาพ
    if (isset($_FILES['club_image']) && $_FILES['club_image']['name'] != "") {
        if ($_FILES['club_image']['error'] == 0) {
            $target_dir = "../../uploads/";

            // ตรวจสอบว่ามีโฟลเดอร์ uploads หรือยัง ถ้าไม่มีให้สร้าง
            if (!file_exists($target_dir)) {
                mkdir($target_dir, 0777, true);
            }

            $original_filename = basename($_FILES["club_image"]["name"]);
            $file_extension = strtolower(pathinfo($original_filename, PATHINFO_EXTENSION));
            
            // อนุญาตเฉพาะไฟล์รูปภาพ
            $allowed_extensions = ["jpg", "jpeg", "png", "gif"];
            if (in_array($file_extension, $allowed_extensions)) {
                // สุ่มชื่อไฟล์ใหม่เพื่อป้องกันชื่อซ้ำ
                $new_filename = time() . "_" . bin2hex(random_bytes(4)) . "." . $file_extension;
                $target_file = $target_dir . $new_filename;

                // ดำเนินการย้ายไฟล์จาก temp ไปยังโฟลเดอร์เป้าหมาย
                if (move_uploaded_file($_FILES["club_image"]["tmp_name"], $target_file)) {
                    $image = $new_filename;
                } else {
                    echo "<script>alert('ไม่สามารถย้ายไฟล์ไปยังโฟลเดอร์เป้าหมายได้ กรุณาลองใหม่อีกครั้ง'); window.history.back(); exit();</script>";
                }
            } else {
                echo "<script>alert('รองรับเฉพาะไฟล์รูปภาพ (JPG, PNG, GIF) เท่านั้น'); window.history.back(); exit();</script>";
            }
        } else {
            // แจ้งเตือนตาม Error Code
            $error_code = $_FILES['club_image']['error'];
            $error_msg = "เกิดข้อผิดพลาดในการอัปโหลด: ";
            switch ($error_code) {
                case 1: $error_msg .= "ไฟล์มีขนาดใหญ่เกินกว่าที่เซิร์ฟเวอร์กำหนด (upload_max_filesize)"; break;
                case 2: $error_msg .= "ไฟล์มีขนาดใหญ่เกินกว่าที่ฟอร์มกำหนด (MAX_FILE_SIZE)"; break;
                case 3: $error_msg .= "อัปโหลดไฟล์ไม่สมบูรณ์ (Partial Upload)"; break;
                case 6: $error_msg .= "ไม่พบโฟลเดอร์ชั่วคราว (Missing Temp Folder)"; break;
                case 7: $error_msg .= "ไม่สามารถเขียนไฟล์ลงดิสก์ได้ (Failed to write to disk)"; break;
                default: $error_msg .= "Error Code: " . $error_code;
            }
            echo "<script>alert('" . addslashes($error_msg) . "'); window.history.back(); exit();</script>";
        }
    }

    // ปรับชื่อคอลัมน์ให้ตรงตาม Database (Club_Image พิมพ์ใหญ่ตัว I)
    $sql = "INSERT INTO club (Name_Club, Description, Club_type, Member, Club_Image) 
            VALUES ('$nameclub', '$desc', '$clubtype', '$member', '$image')";

    $result = mysqli_query($conn, $sql);

    if ($result) {
        echo "<script>alert('สร้างชมรมสำเร็จ'); window.location.href= '../../frontend/admin/Admin.html';</script>";
    } else {
        // หากล้มเหลว ให้แจ้งเตือนและกลับไปหน้าเดิม
        $error_msg = mysqli_error($conn);
        echo "<script>alert('สร้างชมรมไม่สำเร็จ: " . addslashes($error_msg) . "'); window.history.back();</script>";
    }
}

?>