<?php
/**
 * Calligraphy Central - Centralized HTTP Security Headers
 */

// 1. Content Security Policy (CSP)
// Conservative policy allowing local assets, media, styles, inline handlers, and Google Fonts.
$csp_directives = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com https://fonts.googleapis.com",
    "img-src 'self' data:",
    "media-src 'self'",
    "object-src 'none'",
    "frame-ancestors 'self'",
    "base-uri 'self'",
    "form-action 'self'"
];

header("Content-Security-Policy: " . implode("; ", $csp_directives));

// 2. X-Frame-Options (Clickjacking defense)
header("X-Frame-Options: SAMEORIGIN");

// 3. X-Content-Type-Options (MIME-sniffing defense)
header("X-Content-Type-Options: nosniff");

// 4. Referrer-Policy
header("Referrer-Policy: strict-origin-when-cross-origin");

// 5. Permissions-Policy (Restrict unused features)
header("Permissions-Policy: geolocation=(), camera=(), microphone=()");
?>
