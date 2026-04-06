<?php
include "config.php";
$conn = mysqli_connect(DB_Server, DB_User, DB_Password, DB_DatabaseName)
    or die("Can not connect to database");
?>