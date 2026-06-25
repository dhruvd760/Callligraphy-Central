<?php
/**
 * Calligraphy Central - HTTPS Enforcement & Local Bypass
 */

// 1. Detect if the environment is localhost, XAMPP, or loopback IP
$host = $_SERVER['HTTP_HOST'] ?? '';
$remote_ip = $_SERVER['REMOTE_ADDR'] ?? '';

$is_localhost = false;
if (
    $host === 'localhost' ||
    str_starts_with($host, '127.0.0.1') ||
    str_starts_with($host, '[::1]') ||
    $remote_ip === '127.0.0.1' ||
    $remote_ip === '::1' ||
    stripos($host, 'localhost') !== false
) {
    $is_localhost = true;
}

// 2. Detect if the connection uses HTTPS
$is_https = false;
if (isset($_SERVER['HTTPS']) && ($_SERVER['HTTPS'] === 'on' || $_SERVER['HTTPS'] == 1)) {
    $is_https = true;
} elseif (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $is_https = true;
}

if (!$is_localhost) {
    if (!$is_https) {
        // Enforce HTTPS redirect for non-local production environments
        $https_url = "https://" . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];
        header("Location: " . $https_url, true, 301);
        exit();
    } else {
        // Enforce HSTS (Strict-Transport-Security) for HTTPS production requests
        header("Strict-Transport-Security: max-age=31536000; includeSubDomains; preload");
    }
}
?>
