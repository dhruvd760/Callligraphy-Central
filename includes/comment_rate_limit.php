<?php
/**
 * Calligraphy Central - Comment Rate Limiting & Spam Protection
 */

function checkCommentRateLimit($conn, $user_id) {
    $limit = 5;
    $time_window_seconds = 60;

    // 1. Ensure the database table exists dynamically
    $table_created = false;
    try {
        $conn->query("CREATE TABLE IF NOT EXISTS comment_attempts (
            user_id INT NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (user_id),
            INDEX (attempt_time)
        )");
        $table_created = true;
    } catch (Exception $e) {
        error_log("Database comment rate limit table creation failed: " . $e->getMessage() . ". Falling back to session-based tracking.");
    }

    if ($table_created) {
        // Clean up attempts older than time window
        try {
            $stmt_clean = $conn->prepare("DELETE FROM comment_attempts WHERE attempt_time < (NOW() - INTERVAL ? SECOND)");
            if ($stmt_clean) {
                $stmt_clean->bind_param("i", $time_window_seconds);
                $stmt_clean->execute();
                $stmt_clean->close();
            }
        } catch (Exception $e) {
            // Ignore DB error
        }

        // Count attempts for the user within the last 60 seconds
        try {
            $stmt_count = $conn->prepare("SELECT COUNT(*) FROM comment_attempts WHERE user_id = ? AND attempt_time >= (NOW() - INTERVAL ? SECOND)");
            if ($stmt_count) {
                $stmt_count->bind_param("ii", $user_id, $time_window_seconds);
                $stmt_count->execute();
                $stmt_count->bind_result($count);
                $stmt_count->fetch();
                $stmt_count->close();

                if ($count >= $limit) {
                    writeSecurityLog('suspicious_activity', "Comment rate limit exceeded (Attempts: $count)", ['attempts_count' => $count]);
                    return [
                        'locked' => true,
                        'remaining' => $time_window_seconds
                    ];
                }
            }
        } catch (Exception $e) {
            // Fallback if statement execution fails
        }
    }

    // Session-based fallback
    if (session_status() === PHP_SESSION_NONE) {
        include_once __DIR__ . '/session_config.php';
    }

    // Initialize session structure if not present
    if (!isset($_SESSION['comment_attempts'])) {
        $_SESSION['comment_attempts'] = [];
    }

    // Filter session timestamps in the last 60 seconds
    $now = time();
    $_SESSION['comment_attempts'] = array_filter($_SESSION['comment_attempts'], function($timestamp) use ($now, $time_window_seconds) {
        return $timestamp >= ($now - $time_window_seconds);
    });

    if (count($_SESSION['comment_attempts']) >= $limit) {
        writeSecurityLog('suspicious_activity', "Session-based comment rate limit exceeded");
        return [
            'locked' => true,
            'remaining' => $time_window_seconds
        ];
    }

    return ['locked' => false];
}

function recordCommentAttempt($conn, $user_id) {
    try {
        $stmt = $conn->prepare("INSERT INTO comment_attempts (user_id) VALUES (?)");
        if ($stmt) {
            $stmt->bind_param("i", $user_id);
            $stmt->execute();
            $stmt->close();
        }
    } catch (Exception $e) {
        // Fallback
    }

    // Session fallback tracking
    if (session_status() === PHP_SESSION_NONE) {
        include_once __DIR__ . '/session_config.php';
    }

    if (!isset($_SESSION['comment_attempts'])) {
        $_SESSION['comment_attempts'] = [];
    }
    $_SESSION['comment_attempts'][] = time();
}
?>
