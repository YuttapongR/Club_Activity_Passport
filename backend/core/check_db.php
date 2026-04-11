<?php
include "connect_db.php";
$query = "DESCRIBE user";
$result = mysqli_query($conn, $query);
while ($row = mysqli_fetch_assoc($result)) {
    print_r($row);
}
?>