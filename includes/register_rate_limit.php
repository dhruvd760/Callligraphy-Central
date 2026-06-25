<?php
/**
 * Calligraphy Central - Registration Rate Limiting & Abuse Prevention
 */

function checkRegisterRateLimit($conn) {
    $ip_address = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
    $limit = 5;
    $lockout_duration_seconds = 3600; // 1 hour

    // 1. Ensure the database table exists dynamically
    $table_created = false;
    try {
        $conn->query("CREATE TABLE IF NOT EXISTS registration_attempts (
            ip_address VARCHAR(45) NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (ip_address),
            INDEX (attempt_time)
        )");
        $table_created = true;
    } catch (Exception $e) {
        error_log("Database registration rate limit table creation failed: " . $e->getMessage() . ". Falling back to session-based tracking.");
    }

    if ($table_created) {
        // Clean up attempts older than lockout duration
        try {
            $stmt_clean = $conn->prepare("DELETE FROM registration_attempts WHERE attempt_time < (NOW() - INTERVAL ? SECOND)");
            if ($stmt_clean) {
                $stmt_clean->bind_param("i", $lockout_duration_seconds);
                $stmt_clean->execute();
                $stmt_clean->close();
            }
        } catch (Exception $e) {
            // Ignore DB error
        }

        // Count failed attempts for the IP within the last 1 hour
        try {
            $stmt_count = $conn->prepare("SELECT COUNT(*) FROM registration_attempts WHERE ip_address = ? AND attempt_time >= (NOW() - INTERVAL ? SECOND)");
            if ($stmt_count) {
                $stmt_count->bind_param("si", $ip_address, $lockout_duration_seconds);
                $stmt_count->execute();
                $stmt_count->bind_result($count);
                $stmt_count->fetch();
                $stmt_count->close();

                if ($count >= $limit) {
                    writeSecurityLog('suspicious_activity', "Registration lockout triggered (Attempts: $count)", ['attempts_count' => $count]);
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

    // Session-based fallback
    if (session_status() === PHP_SESSION_NONE) {
        include_once __DIR__ . '/session_config.php';
    }

    if (isset($_SESSION['register_lockout_time']) && time() < $_SESSION['register_lockout_time']) {
        $remaining = $_SESSION['register_lockout_time'] - time();
        writeSecurityLog('suspicious_activity', "Session-based registration lockout active ($remaining seconds remaining)", ['remaining_seconds' => $remaining]);
        return [
            'locked' => true,
            'remaining' => $remaining
        ];
    }

    // Clear expired session-based lockout
    if (isset($_SESSION['register_lockout_time']) && time() >= $_SESSION['register_lockout_time']) {
        unset($_SESSION['register_lockout_time']);
        unset($_SESSION['register_attempts']);
    }

    return ['locked' => false];
}

function recordRegistrationAttempt($conn) {
    $ip_address = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
    writeSecurityLog('registration_attempt', "New registration attempt");

    try {
        $stmt = $conn->prepare("INSERT INTO registration_attempts (ip_address) VALUES (?)");
        if ($stmt) {
            $stmt->bind_param("s", $ip_address);
            $stmt->execute();
            $stmt->close();
        }
    } catch (Exception $e) {
        // Fallback to session
    }

    // Always update session tracking as well for defence-in-depth/fallback
    if (session_status() === PHP_SESSION_NONE) {
        include_once __DIR__ . '/session_config.php';
    }

    $_SESSION['register_attempts'] = ($_SESSION['register_attempts'] ?? 0) + 1;
    if ($_SESSION['register_attempts'] >= 5) {
        $_SESSION['register_lockout_time'] = time() + 3600; // 1 hour lockout
    }
}
?>
