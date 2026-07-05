<?php
include_once 'includes/session_config.php';
// Use the exact path to your db_connect file based on your folder structure
include 'includes/db_connect.php'; 
include 'includes/csrf.php';

if (!isset($_SESSION['user_id'])) {
    writeSecurityLog('unauthorized_access', "Unauthenticated request to like_posts.php");
    header("Location: login.php");
    exit();
}

if (isset($_POST['post_id'])) {
    verifyCSRFToken();
    $user_id = $_SESSION['user_id'];
    $post_id = $_POST['post_id'];

    include_once 'includes/RateLimiter.php';
    $rate_limit_check = RateLimiter::checkLikeRateLimit($conn, $user_id);

    if ($rate_limit_check['locked']) {
        if (isset($_SERVER['HTTP_REFERER'])) {
            header("Location: " . $_SERVER['HTTP_REFERER']);
        } else {
            header("Location: gallery.php");
            exit();
        }
        exit();
    }

    // Record the attempt
    RateLimiter::recordLikeAttempt($conn, $user_id);

    // 1. Check if already liked
    $check = $conn->prepare("SELECT like_id FROM likes WHERE user_id = ? AND post_id = ?");
    $check->bind_param("ii", $user_id, $post_id);
    $check->execute();
    $result = $check->get_result();

    if ($result->num_rows > 0) {
        // Already liked -> UNLIKE (Delete)
        $stmt = $conn->prepare("DELETE FROM likes WHERE user_id = ? AND post_id = ?");
        $stmt->bind_param("ii", $user_id, $post_id);
        $stmt->execute();
    } else {
        // Not liked -> LIKE (Insert)
        $stmt = $conn->prepare("INSERT INTO likes (user_id, post_id) VALUES (?, ?)");
        $stmt->bind_param("ii", $user_id, $post_id);
        $stmt->execute();
    }

    // 2. REDIRECT BACK TO GALLERY (Anchors directly to the post they clicked!)
     if (isset($_SERVER['HTTP_REFERER'])) {
        header("Location: " . $_SERVER['HTTP_REFERER']);
    } else {
        // Fallback just in case
        header("Location: gallery.php");
        exit();
    }
    exit();
}
?>