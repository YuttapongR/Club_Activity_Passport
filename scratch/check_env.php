<?php
include "backend/core/connect_db.php";

echo "PHP User: " . get_current_user() . "\n";
echo "Uploads dir exists: " . (file_exists("uploads") ? "Yes" : "No") . "\n";
echo "Uploads dir writable: " . (is_writable("uploads") ? "Yes" : "No") . "\n";

$result = mysqli_query($conn, "DESCRIBE club");
echo "Table 'club' structure:\n";
while ($row = mysqli_fetch_assoc($result)) {
    print_r($row);
}
?>