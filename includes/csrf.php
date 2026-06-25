<?php
/**
 * CSRF Protection Helpers
 */

function generateCSRFToken() {
    // Ensure session is started via centralized configuration
    if (session_status() === PHP_SESSION_NONE) {
        include_once __DIR__ . '/session_config.php';
    }
    
    // Store the token in $_SESSION['csrf_token'] if it does not already exist
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    
    // Return the token
    return $_SESSION['csrf_token'];
}

function verifyCSRFToken() {
    // Ensure session is started for verification via centralized configuration
    if (session_status() === PHP_SESSION_NONE) {
        include_once __DIR__ . '/session_config.php';
    }
    
    // Validate that $_POST['csrf_token'] exists
    if (!isset($_POST['csrf_token']) || empty($_SESSION['csrf_token'])) {
        writeSecurityLog('invalid_csrf', "CSRF token verification failed: Missing token", ['post_keys' => array_keys($_POST)]);
        http_response_code(400);
        die("CSRF token verification failed: Missing token.");
    }
    
    // Compare it against $_SESSION['csrf_token'] using hash_equals
    if (!hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'])) {
        writeSecurityLog('invalid_csrf', "CSRF token verification failed: Invalid token", ['post_keys' => array_keys($_POST)]);
        http_response_code(403);
        die("CSRF token verification failed: Invalid token.");
    }
}
?>
