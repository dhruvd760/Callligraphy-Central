<?php
/**
 * Calligraphy Central - Unified Rate Limiter
 * Handles rate limiting for login, register, comments, and likes.
 */

class RateLimiter {
    // Shared private method for generic check (register, comment, like)
    private static function checkGeneric($conn, $table, $column, $value, $limit, $window_seconds, $session_key, $type) {
        $table_created = false;
        $type_map = [
            'register' => "ip_address VARCHAR(45) NOT NULL, attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, INDEX (ip_address), INDEX (attempt_time)",
            'comment'  => "user_id INT NOT NULL, attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, INDEX (user_id), INDEX (attempt_time)",
            'like'     => "user_id INT NOT NULL, attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, INDEX (user_id), INDEX (attempt_time)",
        ];
        
        try {
            $conn->query("CREATE TABLE IF NOT EXISTS {$table} ({$type_map[$type]})");
            $table_created = true;
        } catch (Exception $e) {
            error_log("Database {$type} rate limit table creation failed: " . $e->getMessage() . ". Falling back to session-based tracking.");
        }

        if ($table_created) {
            try {
                $stmt_clean = $conn->prepare("DELETE FROM {$table} WHERE attempt_time < (NOW() - INTERVAL ? SECOND)");
                if ($stmt_clean) {
                    $stmt_clean->bind_param("i", $window_seconds);
                    $stmt_clean->execute();
                    $stmt_clean->close();
                }
            } catch (Exception $e) {}

            try {
                $stmt_count = $conn->prepare("SELECT COUNT(*) FROM {$table} WHERE {$column} = ? AND attempt_time >= (NOW() - INTERVAL ? SECOND)");
                if ($stmt_count) {
                    // $value could be string (ip) or int (user_id)
                    $type_char = is_int($value) ? "i" : "s";
                    $stmt_count->bind_param("{$type_char}i", $value, $window_seconds);
                    $stmt_count->execute();
                    $stmt_count->bind_result($count);
                    $stmt_count->fetch();
                    $stmt_count->close();

                    if ($count >= $limit) {
                        writeSecurityLog('suspicious_activity', ucfirst($type) . " rate limit exceeded (Attempts: $count)", ['attempts_count' => $count]);
                        return ['locked' => true, 'remaining' => $window_seconds];
                    }
                }
            } catch (Exception $e) {}
        }

        // Session-based fallback
        if (session_status() === PHP_SESSION_NONE) {
            include_once __DIR__ . '/session_config.php';
        }

        if ($type === 'register') {
            if (isset($_SESSION[$session_key . '_lockout_time']) && time() < $_SESSION[$session_key . '_lockout_time']) {
                $remaining = $_SESSION[$session_key . '_lockout_time'] - time();
                writeSecurityLog('suspicious_activity', "Session-based registration lockout active ($remaining seconds remaining)", ['remaining_seconds' => $remaining]);
                return ['locked' => true, 'remaining' => $remaining];
            }
            if (isset($_SESSION[$session_key . '_lockout_time']) && time() >= $_SESSION[$session_key . '_lockout_time']) {
                unset($_SESSION[$session_key . '_lockout_time']);
                unset($_SESSION[$session_key . '_attempts']);
            }
        } else {
            // Like & Comment session arrays
            if (!isset($_SESSION[$session_key])) $_SESSION[$session_key] = [];
            $now = time();
            $_SESSION[$session_key] = array_filter($_SESSION[$session_key], function($timestamp) use ($now, $window_seconds) {
                return $timestamp >= ($now - $window_seconds);
            });
            if (count($_SESSION[$session_key]) >= $limit) {
                writeSecurityLog('suspicious_activity', "Session-based {$type} rate limit exceeded");
                return ['locked' => true, 'remaining' => $window_seconds];
            }
        }

        return ['locked' => false];
    }

    private static function recordGeneric($conn, $table, $column, $value, $session_key, $type) {
        if ($type === 'register') {
            writeSecurityLog('registration_attempt', "New registration attempt");
        }

        try {
            $stmt = $conn->prepare("INSERT INTO {$table} ({$column}) VALUES (?)");
            if ($stmt) {
                $type_char = is_int($value) ? "i" : "s";
                $stmt->bind_param($type_char, $value);
                $stmt->execute();
                $stmt->close();
            }
        } catch (Exception $e) {}

        if (session_status() === PHP_SESSION_NONE) {
            include_once __DIR__ . '/session_config.php';
        }

        if ($type === 'register') {
            $_SESSION[$session_key . '_attempts'] = ($_SESSION[$session_key . '_attempts'] ?? 0) + 1;
            if ($_SESSION[$session_key . '_attempts'] >= 5) {
                $_SESSION[$session_key . '_lockout_time'] = time() + 3600;
            }
        } else {
            if (!isset($_SESSION[$session_key])) $_SESSION[$session_key] = [];
            $_SESSION[$session_key][] = time();
        }
    }

    // -- REGISTER --
    public static function checkRegisterRateLimit($conn) {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        return self::checkGeneric($conn, 'registration_attempts', 'ip_address', $ip, 5, 3600, 'register', 'register');
    }
    public static function recordRegistrationAttempt($conn) {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        self::recordGeneric($conn, 'registration_attempts', 'ip_address', $ip, 'register', 'register');
    }

    // -- COMMENT --
    public static function checkCommentRateLimit($conn, $user_id) {
        return self::checkGeneric($conn, 'comment_attempts', 'user_id', $user_id, 5, 60, 'comment_attempts', 'comment');
    }
    public static function recordCommentAttempt($conn, $user_id) {
        self::recordGeneric($conn, 'comment_attempts', 'user_id', $user_id, 'comment_attempts', 'comment');
    }

    // -- LIKE --
    public static function checkLikeRateLimit($conn, $user_id) {
        return self::checkGeneric($conn, 'like_attempts', 'user_id', $user_id, 10, 30, 'like_attempts', 'like');
    }
    public static function recordLikeAttempt($conn, $user_id) {
        self::recordGeneric($conn, 'like_attempts', 'user_id', $user_id, 'like_attempts', 'like');
    }

    // -- LOGIN --
    public static function checkLoginRateLimit($conn, $email) {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        $limit = 5;
        $window = 900;
        
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
        } catch (Exception $e) {}

        if ($table_created) {
            try {
                $stmt = $conn->prepare("DELETE FROM login_attempts WHERE attempt_time < (NOW() - INTERVAL ? SECOND)");
                if ($stmt) {
                    $stmt->bind_param("i", $window);
                    $stmt->execute();
                    $stmt->close();
                }
            } catch (Exception $e) {}

            try {
                $stmt = $conn->prepare("SELECT COUNT(*) FROM login_attempts WHERE (ip_address = ? OR email = ?) AND attempt_time >= (NOW() - INTERVAL ? SECOND)");
                if ($stmt) {
                    $stmt->bind_param("ssi", $ip, $email, $window);
                    $stmt->execute();
                    $stmt->bind_result($count);
                    $stmt->fetch();
                    $stmt->close();

                    if ($count >= $limit) {
                        writeSecurityLog('suspicious_activity', "Login lockout triggered for email '$email' (Attempts: $count)", ['email' => $email, 'attempts_count' => $count]);
                        return ['locked' => true, 'remaining' => $window];
                    }
                }
            } catch (Exception $e) {}
        }

        if (session_status() === PHP_SESSION_NONE) include_once __DIR__ . '/session_config.php';
        
        if (isset($_SESSION['lockout_time']) && time() < $_SESSION['lockout_time']) {
            $rem = $_SESSION['lockout_time'] - time();
            return ['locked' => true, 'remaining' => $rem];
        }
        if (isset($_SESSION['lockout_time']) && time() >= $_SESSION['lockout_time']) {
            unset($_SESSION['lockout_time']);
            unset($_SESSION['failed_attempts']);
        }
        return ['locked' => false];
    }

    public static function recordFailedLoginAttempt($conn, $email) {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        writeSecurityLog('failed_login', "Failed login attempt for email '$email'", ['email' => $email]);
        try {
            $stmt = $conn->prepare("INSERT INTO login_attempts (ip_address, email) VALUES (?, ?)");
            if ($stmt) {
                $stmt->bind_param("ss", $ip, $email);
                $stmt->execute();
                $stmt->close();
            }
        } catch (Exception $e) {}

        if (session_status() === PHP_SESSION_NONE) include_once __DIR__ . '/session_config.php';
        $_SESSION['failed_attempts'] = ($_SESSION['failed_attempts'] ?? 0) + 1;
        if ($_SESSION['failed_attempts'] >= 5) {
            $_SESSION['lockout_time'] = time() + 900;
        }
    }

    public static function clearLoginAttempts($conn, $email) {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        try {
            $stmt = $conn->prepare("DELETE FROM login_attempts WHERE ip_address = ? OR email = ?");
            if ($stmt) {
                $stmt->bind_param("ss", $ip, $email);
                $stmt->execute();
                $stmt->close();
            }
        } catch (Exception $e) {}

        if (session_status() === PHP_SESSION_ACTIVE) {
            unset($_SESSION['failed_attempts']);
            unset($_SESSION['lockout_time']);
        }
    }
}
?>
