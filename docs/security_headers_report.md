# Security Headers Hardening Report

This report documents the design decisions and implementation details for the system-wide integration of HTTP security headers in Calligraphy Central.

---

## 1. Executive Summary

We have integrated a centralized security headers configuration to restrict unauthorized execution vectors, protect against UI clickjacking, prevent MIME-sniffing exploits, and control cross-origin data exposure. The implementation maintains full visual and functional parity with the legacy interface.

---

## 2. Configured Headers and Rationale

The HTTP headers are defined in the centralized module [includes/security_headers.php](file:///c:/xampp/htdocs/calligraphy_project/includes/security_headers.php) and applied globally:

### 2.1 Content-Security-Policy (CSP)
A conservative policy is configured to prevent unauthorized injection attacks (such as cross-site scripting) while ensuring that inline styling and core event handlers run without interruption:
*   `default-src 'self'`: Restricts resource fetching to the application's origin by default.
*   `script-src 'self' 'unsafe-inline'`: Permits executing scripts hosted on the application domain, along with inline handlers. This directive is required to support the interactive video preview hover features in `admin_dashboard.php` (`onmouseover`, `onmouseout`, `onclick`, `ontouchstart`).
*   `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com`: Permits styling from local stylesheets, inline rules (used extensively in layouts and forms), and Google Fonts services.
*   `font-src 'self' https://fonts.gstatic.com https://fonts.googleapis.com`: Whitelists local font assets and Google Fonts' font delivery domains to support standard typography styles.
*   `img-src 'self' data:`: Permits rendering local images and data URIs.
*   `media-src 'self'`: Restricts video/audio sources to the application domain (`uploads/` folder).
*   `object-src 'none'`: Disables plugin loading (e.g. Flash) to eliminate related execution vectors.
*   `frame-ancestors 'self'`: Restricts framing of the site to the application itself.
*   `base-uri 'self'`: Constrains the document's `<base>` element to the current origin.
*   `form-action 'self'`: Restricts form target endpoints strictly to the local application.

### 2.2 X-Frame-Options
*   **Value**: `SAMEORIGIN`
*   **Purpose**: Prevents the application from being loaded inside `<iframe>` elements on third-party origins, neutralizing Clickjacking vulnerabilities.

### 2.3 X-Content-Type-Options
*   **Value**: `nosniff`
*   **Purpose**: Forces browsers to strictly adhere to the MIME types sent in the `Content-Type` header, disabling MIME-sniffing behaviors that could execute hidden scripts (e.g., in uploaded media).

### 2.4 Referrer-Policy
*   **Value**: `strict-origin-when-cross-origin`
*   **Purpose**: Ensures that referrer headers contain full path details on same-origin requests, but only send the origin component (or withhold completely) on cross-origin requests, preventing URL parameter leakage.

### 2.5 Permissions-Policy
*   **Value**: `geolocation=(), camera=(), microphone=()`
*   **Purpose**: Disables browser APIs for device geolocation, camera access, and audio capture, reducing the application's client device feature-exposure footprint.

---

## 3. Global Inclusion Architecture

To ensure the security headers are present on all application routes (including HTML view pages, action redirects, and form processors), we integrated the configuration globally:
*   The headers module is included at the top of [includes/session_config.php](file:///c:/xampp/htdocs/calligraphy_project/includes/session_config.php):
    ```php
    // Load security headers globally
    include_once __DIR__ . '/security_headers.php';
    ```
*   Since all page controllers (e.g. `gallery.php`, `login.php`, `delete_post.php`) require session verification, they depend on `session_config.php` as their first execution block. This guarantees that headers are sent before any HTML content or response body is emitted.

---

## 4. Verification and Functional Compatibility

*   **Syntax Checks**: Verified with the local compiler check (`php -l`). All PHP scripts, including [includes/security_headers.php](file:///c:/xampp/htdocs/calligraphy_project/includes/security_headers.php) and [includes/session_config.php](file:///c:/xampp/htdocs/calligraphy_project/includes/session_config.php), compiled without errors.
*   **Functional Compatibility**: Google Fonts load correctly, video hover animations on the dashboard execute normally, and CSS alignments remain perfectly intact.
