<?php
include_once 'includes/session_config.php';
include 'includes/db_connect.php';
include 'includes/csrf.php';

// If a guest tries to access this file directly via the URL, stop them immediately.
if (!isset($_SESSION['user_id'])) {
    writeSecurityLog('unauthorized_access', "Unauthenticated request to submit_comments.php");
    // Redirect them to the login page instead of just showing a blank error screen
    header("Location: login.php");
    exit();
}

// ... the rest of the insert logic goes here ...
if (isset($_POST['post_id']) && isset($_POST['comment_text'])) {
    verifyCSRFToken();
    $user_id = $_SESSION['user_id'];
    $post_id = $_POST['post_id'];
    $comment = $_POST['comment_text']; // Sanitize input!

    include_once 'includes/RateLimiter.php';
    $rate_limit_check = RateLimiter::checkCommentRateLimit($conn, $user_id);

    if ($rate_limit_check['locked']) {
        header("Location: view_post.php?id=" . $post_id . "&error=rate_limit");
        exit();
    }

    // Record the comment attempt
    RateLimiter::recordCommentAttempt($conn, $user_id);

    // Ensure the comment isn't just empty spaces
    if (!empty(trim($comment))) {
        $stmt = $conn->prepare("INSERT INTO comments (user_id, post_id, comment_text) VALUES (?, ?, ?)");
        $stmt->bind_param("iis", $user_id, $post_id, $comment);
        $stmt->execute();
    }

    // REDIRECT BACK TO GALLERY
    header("Location: view_post.php?id=" . $post_id);
    exit();
}
?>
