<?php
include "connect_db.php";
$query = "ALTER TABLE user ADD COLUMN Role ENUM('user', 'admin') DEFAULT 'user' NOT NULL";
if (mysqli_query($conn, $query)) {
    echo "Column Role added.";
} else {
    echo "Error: " . mysqli_error($conn);
}
?>