<?php
/**
 * Calligraphy Central - Login Rate Limiting & Brute-Force Protection
 */

function checkLoginRateLimit($conn, $email) {
    $ip_address = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
    $limit = 5;
    $lockout_duration_seconds = 900; // 15 minutes

    // 1. Ensure the database table exists dynamically
    $table_created = false;
    try {
        $conn->query("CREATE TABLE IF NOT EXISTS login_attempts (
            ip_address VARCHAR(45) NOT NULL,
            email VARCHAR(100) NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (ip_address),
            INDEX (email),
            INDEX (attempt_time)
        )");
        $table_created = true;
    } catch (Exception $e) {
        error_log("Database rate limit table creation failed: " . $e->getMessage() . ". Falling back to session-based tracking.");
    }

    if ($table_created) {
        // Clean up attempts older than lockout duration
        try {
            $stmt_clean = $conn->prepare("DELETE FROM login_attempts WHERE attempt_time < (NOW() - INTERVAL ? SECOND)");
            if ($stmt_clean) {
                $stmt_clean->bind_param("i", $lockout_duration_seconds);
                $stmt_clean->execute();
                $stmt_clean->close();
            }
        } catch (Exception $e) {
            // Ignore DB error
        }

        // Count failed attempts for either IP or email within the last 15 minutes
        try {
            $stmt_count = $conn->prepare("SELECT COUNT(*) FROM login_attempts WHERE (ip_address = ? OR email = ?) AND attempt_time >= (NOW() - INTERVAL ? SECOND)");
            if ($stmt_count) {
                $stmt_count->bind_param("ssi", $ip_address, $email, $lockout_duration_seconds);
                $stmt_count->execute();
                $stmt_count->bind_result($count);
                $stmt_count->fetch();
                $stmt_count->close();

                if ($count >= $limit) {
                    writeSecurityLog('suspicious_activity', "Login lockout triggered for email '$email' (Attempts: $count)", ['email' => $email, 'attempts_count' => $count]);
                    return [
                        'locked' => true,
                        'remaining' => $lockout_duration_seconds
                    ];
                }
            }
        } catch (Exception $e) {
            // Fallback if statement execution fails
        }
    }

    // Session-based fallback (run concurrently or if DB fails)
    if (session_status() === PHP_SESSION_NONE) {
        include_once __DIR__ . '/session_config.php';
    }

    if (isset($_SESSION['lockout_time']) && time() < $_SESSION['lockout_time']) {
        $remaining = $_SESSION['lockout_time'] - time();
        writeSecurityLog('suspicious_activity', "Session-based login lockout active ($remaining seconds remaining)", ['remaining_seconds' => $remaining]);
        return [
            'locked' => true,
            'remaining' => $remaining
        ];
    }

    // Clear expired session-based lockout
    if (isset($_SESSION['lockout_time']) && time() >= $_SESSION['lockout_time']) {
        unset($_SESSION['lockout_time']);
        unset($_SESSION['failed_attempts']);
    }

    return ['locked' => false];
}

function recordFailedLoginAttempt($conn, $email) {
    $ip_address = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
    writeSecurityLog('failed_login', "Failed login attempt for email '$email'", ['email' => $email]);

    $recorded_in_db = false;
    try {
        $stmt = $conn->prepare("INSERT INTO login_attempts (ip_address, email) VALUES (?, ?)");
        if ($stmt) {
            $stmt->bind_param("ss", $ip_address, $email);
            $stmt->execute();
            $stmt->close();
            $recorded_in_db = true;
        }
    } catch (Exception $e) {
        // Fallback to session
    }

    // Always update session tracking as well for defence-in-depth/fallback
    if (session_status() === PHP_SESSION_NONE) {
        include_once __DIR__ . '/session_config.php';
    }

    $_SESSION['failed_attempts'] = ($_SESSION['failed_attempts'] ?? 0) + 1;
    if ($_SESSION['failed_attempts'] >= 5) {
        $_SESSION['lockout_time'] = time() + 900; // 15 minutes
    }
}

function clearLoginAttempts($conn, $email) {
    $ip_address = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';

    try {
        $stmt = $conn->prepare("DELETE FROM login_attempts WHERE ip_address = ? OR email = ?");
        if ($stmt) {
            $stmt->bind_param("ss", $ip_address, $email);
            $stmt->execute();
            $stmt->close();
        }
    } catch (Exception $e) {
        // Ignore DB error
    }

    // Clear session tracking
    if (session_status() === PHP_SESSION_ACTIVE) {
        unset($_SESSION['failed_attempts']);
        unset($_SESSION['lockout_time']);
    }
}
?>
