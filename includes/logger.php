<?php
/**
 * Calligraphy Central - Reusable Security Logger Utility
 */

function writeSecurityLog($event_type, $message, $metadata = []) {
    $ip_address = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
    $user_id = $_SESSION['user_id'] ?? 'Anonymous';
    $timestamp = date('Y-m-d H:i:s');

    // 1. Sanitize metadata to never log passwords, CSRF tokens, or secrets
    $sanitized_metadata = [];
    foreach ($metadata as $key => $value) {
        if (preg_match('/(password|pwd|secret|token|csrf|pass)/i', $key)) {
            $sanitized_metadata[$key] = '[REDACTED]';
        } else {
            $sanitized_metadata[$key] = $value;
        }
    }

    $metadata_str = !empty($sanitized_metadata) ? ' | Metadata: ' . json_encode($sanitized_metadata) : '';
    $log_entry = sprintf(
        "[%s] [SECURITY] [Event: %s] [IP: %s] [User ID: %s] - %s%s\n",
        $timestamp,
        strtoupper($event_type),
        $ip_address,
        $user_id,
        $message,
        $metadata_str
    );

    // 2. Ensure logs folder exists and is protected from web access
    $logs_dir = __DIR__ . '/../logs';
    if (!file_exists($logs_dir)) {
        mkdir($logs_dir, 0750, true);
    }

    // Write .htaccess to block direct access if it doesn't exist
    $htaccess_path = $logs_dir . '/.htaccess';
    if (!file_exists($htaccess_path)) {
        file_put_contents($htaccess_path, "Deny from all\n");
    }

    // 3. Write to custom security log file
    $log_file = $logs_dir . '/security.log';
    error_log($log_entry, 3, $log_file);

    // 4. Also write to standard PHP system error log for redundancy
    error_log(sprintf("[SECURITY] [%s] %s%s", strtoupper($event_type), $message, $metadata_str));
}
?>
