<?php
include_once 'includes/session_config.php';
include 'includes/db_connect.php';
include 'includes/csrf.php';

// Verify authentication
if (!isset($_SESSION['user_id'])) {
    writeSecurityLog('unauthorized_access', "Unauthenticated request to delete a post", [
        'post_id' => $_POST['id'] ?? 'unknown'
    ]);
    header("Location: login.php");
    exit();
}

// 1. Verify CSRF token
verifyCSRFToken();

// 2. Check if ID is provided
if (!isset($_POST['id'])) {
    header("Location: gallery.php");
    exit();
}

$post_id = $_POST['id'];
$current_user_id = $_SESSION['user_id'];
$user_role = $_SESSION['role'] ?? 'user'; // Default to 'user' if role is missing

// 2. Fetch the post to check ownership
$stmt = $conn->prepare("SELECT user_id, file_name FROM posts WHERE post_id = ?");
$stmt->bind_param("i", $post_id);
$stmt->execute();
$result = $stmt->get_result();
$post = $result->fetch_assoc();

// If post doesn't exist
if (!$post) {
    die("Post not found.");
}

// 3. CHECK PERMISSION
// Allow delete if: (User owns the post) OR (User is Admin)
if ($post['user_id'] == $current_user_id || $user_role === 'admin') {

    // A. Delete the file from the folder
    $file_path = "uploads/" . $post['file_name'];
    if (file_exists($file_path)) {
        unlink($file_path);
    }

    // B. Delete from Database
    $del_stmt = $conn->prepare("DELETE FROM posts WHERE post_id = ?");
    $del_stmt->bind_param("i", $post_id);

    if ($del_stmt->execute()) {
        // We decide where to go based on the ROLE, not the link.
        
        if ($user_role === 'admin') {
            header("Location: admin_dashboard.php?");
        } else {
            // Regular users go to Gallery
            header("Location: my_posts.php?");
        }
        exit();
        
    } else {
        error_log("Database error in delete_post.php: " . $conn->error);
        die("An error occurred while deleting the record.");
    }

} else {
    // If someone tries to hack/delete a post not theirs
    writeSecurityLog('unauthorized_access', "User attempted to delete a post they do not own", [
        'post_id' => $post_id,
        'owner_id' => $post['user_id']
    ]);
    die("Access Denied: You do not own this post.");
}
?>