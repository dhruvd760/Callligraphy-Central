<?php
/**
 * Calligraphy Central - Centralized Session Security Hardening
 */

// Enforce HTTPS in production environments first
include_once __DIR__ . '/https_enforcement.php';

// Load security headers globally
include_once __DIR__ . '/security_headers.php';

// Load security logger globally
include_once __DIR__ . '/logger.php';

if (session_status() === PHP_SESSION_NONE) {
    // 1. Determine if HTTPS is active on the server
    $is_secure = false;
    if (isset($_SERVER['HTTPS']) && ($_SERVER['HTTPS'] === 'on' || $_SERVER['HTTPS'] == 1)) {
        $is_secure = true;
    } elseif (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
        $is_secure = true;
    }

    // 2. Configure session cookie parameters (HttpOnly, SameSite=Strict, Secure=true conditionally)
    session_set_cookie_params([
        'lifetime' => 0,                 // Expires when browser closes
        'path' => '/',                   // Available across the whole domain
        'domain' => '',                  // Default current host
        'secure' => $is_secure,          // Only send over HTTPS if enabled
        'httponly' => true,              // Prevent JavaScript access to session cookie
        'samesite' => 'Strict'           // Prevent CSRF by blocking cross-site cookie attachment
    ]);

    // 3. Enforce session ini hardening parameters
    ini_set('session.use_only_cookies', 1); // Prevent session ID passing in URLs
    ini_set('session.use_strict_mode', 1);   // Prevent session fixation by rejecting uninitialized session IDs

    // 4. Initialize session
    session_start();
}

/**
 * Regenerates the session identifier securely to prevent session fixation.
 */
function secureSessionRegenerate() {
    if (session_status() === PHP_SESSION_ACTIVE) {
        session_regenerate_id(true);
    }
}
?>
