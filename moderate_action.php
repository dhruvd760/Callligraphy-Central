<?php
include_once 'includes/session_config.php';
include 'includes/db_connect.php';
include 'includes/csrf.php';

// Verify authentication and Admin role
if (!isset($_SESSION['user_id']) || !isset($_SESSION['role']) || $_SESSION['role'] !== 'admin') {
    writeSecurityLog('unauthorized_access', "Non-admin attempted to use moderate_action.php", [
        'user_id' => $_SESSION['user_id'] ?? 'unknown',
        'post_id' => $_POST['id'] ?? 'unknown'
    ]);
    header("Location: login.php");
    exit();
}

// 1. Verify CSRF token
verifyCSRFToken();

// 2. Check if ID and action are provided
if (!isset($_POST['id']) || !isset($_POST['action'])) {
    header("Location: admin_dashboard.php");
    exit();
}

$post_id = $_POST['id'];
$action = $_POST['action'];

// 3. Fetch the post to check if it exists
$stmt = $conn->prepare("SELECT file_name FROM posts WHERE post_id = ?");
$stmt->bind_param("i", $post_id);
$stmt->execute();
$result = $stmt->get_result();
$post = $result->fetch_assoc();

if (!$post) {
    header("Location: admin_dashboard.php?error=not_found");
    exit();
}

if ($action === 'reject') {
    // Reject: Delete file and record
    $file_path = "uploads/" . $post['file_name'];
    if (file_exists($file_path)) {
        unlink($file_path);
    }

    $del_stmt = $conn->prepare("DELETE FROM posts WHERE post_id = ?");
    $del_stmt->bind_param("i", $post_id);

    if ($del_stmt->execute()) {
        header("Location: admin_dashboard.php?msg=rejected");
        exit();
    } else {
        error_log("Database error in moderate_action.php (reject): " . $conn->error);
        header("Location: admin_dashboard.php?error=db_error");
        exit();
    }
} else {
    // Invalid action
    header("Location: admin_dashboard.php");
    exit();
}
exit();
?>
