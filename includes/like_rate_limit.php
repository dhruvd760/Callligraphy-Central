<?php
/**
 * Calligraphy Central - Like Rate Limiting & Abuse Prevention
 */

function checkLikeRateLimit($conn, $user_id) {
    $limit = 10;
    $time_window_seconds = 30;

    // 1. Ensure the database table exists dynamically
    $table_created = false;
    try {
        $conn->query("CREATE TABLE IF NOT EXISTS like_attempts (
            user_id INT NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (user_id),
            INDEX (attempt_time)
        )");
        $table_created = true;
    } catch (Exception $e) {
        error_log("Database like rate limit table creation failed: " . $e->getMessage() . ". Falling back to session-based tracking.");
    }

    if ($table_created) {
        // Clean up attempts older than time window
        try {
            $stmt_clean = $conn->prepare("DELETE FROM like_attempts WHERE attempt_time < (NOW() - INTERVAL ? SECOND)");
            if ($stmt_clean) {
                $stmt_clean->bind_param("i", $time_window_seconds);
                $stmt_clean->execute();
                $stmt_clean->close();
            }
        } catch (Exception $e) {
            // Ignore DB error
        }

        // Count attempts for the user within the last 30 seconds
        try {
            $stmt_count = $conn->prepare("SELECT COUNT(*) FROM like_attempts WHERE user_id = ? AND attempt_time >= (NOW() - INTERVAL ? SECOND)");
            if ($stmt_count) {
                $stmt_count->bind_param("ii", $user_id, $time_window_seconds);
                $stmt_count->execute();
                $stmt_count->bind_result($count);
                $stmt_count->fetch();
                $stmt_count->close();

                if ($count >= $limit) {
                    writeSecurityLog('suspicious_activity', "Like rate limit exceeded (Attempts: $count)", ['attempts_count' => $count]);
                    return [
                        'locked' => true,
                        'remaining' => $time_window_seconds
                    ];
                }
            }
        } catch (Exception $e) {
            // Fallback
        }
    }

    // Session-based fallback
    if (session_status() === PHP_SESSION_NONE) {
        include_once __DIR__ . '/session_config.php';
    }

    if (!isset($_SESSION['like_attempts'])) {
        $_SESSION['like_attempts'] = [];
    }

    // Filter session timestamps in the last 30 seconds
    $now = time();
    $_SESSION['like_attempts'] = array_filter($_SESSION['like_attempts'], function($timestamp) use ($now, $time_window_seconds) {
        return $timestamp >= ($now - $time_window_seconds);
    });

    if (count($_SESSION['like_attempts']) >= $limit) {
        writeSecurityLog('suspicious_activity', "Session-based like rate limit exceeded");
        return [
            'locked' => true,
            'remaining' => $time_window_seconds
        ];
    }

    return ['locked' => false];
}

function recordLikeAttempt($conn, $user_id) {
    try {
        $stmt = $conn->prepare("INSERT INTO like_attempts (user_id) VALUES (?)");
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

    if (!isset($_SESSION['like_attempts'])) {
        $_SESSION['like_attempts'] = [];
    }
    $_SESSION['like_attempts'][] = time();
}
?>
