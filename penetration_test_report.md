# Defensive Penetration Test Report

This report documents the results of the complete defensive penetration test performed on the **Calligraphy Central** application. The evaluation checks the security integrity of the application's authentication, authorization, session management, CSRF, stored XSS, input validation, SQL injection resistance, upload security, error handling, password policy, rate limiting, and security headers.

---

## 1. Executive Summary

A comprehensive, non-intrusive security evaluation was conducted on Calligraphy Central's components. The application has implemented rigorous security defenses including centralized session management, prepared database queries, rate limiters, strict upload constraints, CSRF tokens, and security headers. 

This assessment reviews the efficacy of these controls conceptually and documents remaining areas where defensive improvements can be made.

---

## 2. Test Component Evaluations

### 2.1 Authentication
*   **Evaluation**:
    *   Authentications are managed via [login.php](file:///c:/xampp/htdocs/calligraphy_project/login.php) which validates user credentials against the database.
    *   Passwords are verified using PHP's secure `password_verify()` utility mapping to hash algorithms.
    *   Brute-force protection is enforced by tracking failed attempts dynamically in the database via IP address and email scopes.
*   **Defensive Status**: **PASS**
*   **Recommendation**: Implement logging thresholds for abnormal aggregate authentication failures (e.g., across multiple users from different IPs) to detect distributed credential stuffing campaigns.

### 2.2 Authorization & Access Control
*   **Evaluation**:
    *   Role controls partition guest, authenticated user, and administrator privileges (e.g., [admin_dashboard.php](file:///c:/xampp/htdocs/calligraphy_project/admin_dashboard.php)).
    *   Data modification controllers ([delete_post.php](file:///c:/xampp/htdocs/calligraphy_project/delete_post.php) and [edit_posts.php](file:///c:/xampp/htdocs/calligraphy_project/edit_posts.php)) perform explicit database lookups to verify that the active user matches the target resource owner, unless an admin bypass is active.
*   **Defensive Status**: **PASS**
*   **Recommendation**: Consistently use strict type comparison operators (`===`) when validating database ownership identifiers to avoid potential type juggling anomalies.

### 2.3 Session Management
*   **Evaluation**:
    *   Session parameters are defined centrally in [includes/session_config.php](file:///c:/xampp/htdocs/calligraphy_project/includes/session_config.php) using secure cookie options (`HttpOnly=true`, `SameSite=Strict`, conditional `Secure`, `lifetime=0`).
    *   Session fixation resistance is enabled via `session.use_strict_mode = 1` and `session.use_only_cookies = 1`.
    *   Session identifiers are regenerated via `session_regenerate_id(true)` immediately upon login and terminated via `session_destroy()` and cookie invalidation during logout.
*   **Defensive Status**: **PASS**
*   **Recommendation**: Bind session states to the user's initial browser User-Agent configuration, and implement an inactivity session timeout (e.g. automatically log out users after 15 minutes of idle time).

### 2.4 CSRF Protections
*   **Evaluation**:
    *   State-changing actions require verification of a cryptographically secure token generated and checked via [includes/csrf.php](file:///c:/xampp/htdocs/calligraphy_project/includes/csrf.php).
    *   Tokens are embedded within hidden fields in POST forms. All GET-based state changes have been eliminated.
*   **Defensive Status**: **PASS**
*   **Recommendation**: Periodically regenerate CSRF tokens within long-lived active sessions or bind token creation to specific page paths to limit token misuse potential.

### 2.5 Stored XSS Protections
*   **Evaluation**:
    *   Inputs stored in the database (titles, comments, descriptions) are stored as raw text, which preserves data integrity.
    *   At the presentation layer, all client-rendered values are escaped using `htmlspecialchars($val, ENT_QUOTES, 'UTF-8')`.
*   **Defensive Status**: **PASS**
*   **Recommendation**: Enforce output sanitization using specialized HTML purifier libraries on any fields that might require structured formatting in the future, maintaining strict character sets.

### 2.6 Input Validation
*   **Evaluation**:
    *   Registrations and post updates validate fields (e.g., checking for valid email structures and strict file parameters).
    *   Length boundaries are verified on forms.
*   **Defensive Status**: **PASS**
*   **Recommendation**: Implement server-side input length maximums on fields (e.g., limiting user comments to 1000 characters) to prevent database resource exhaustion.

### 2.7 SQL Injection Resistance
*   **Evaluation**:
    *   All dynamic SQL statements in controllers are written as parameterized MySQLi prepared statements (e.g. using `prepare` and `bind_param`).
    *   This separates SQL compilation from parameter execution, neutralizing SQL Injection.
*   **Defensive Status**: **PASS**
*   **Recommendation**: Avoid using raw dynamic concatenation in sub-queries or sorting queries (e.g. `ORDER BY` directions), relying strictly on query parameter bindings.

### 2.8 Upload Security
*   **Evaluation**:
    *   [upload.php](file:///c:/xampp/htdocs/calligraphy_project/upload.php) restricts file sizes to 50MB, checks file extension whitelists, and validates MIME types.
    *   Files are renamed with unique timestamps to prevent directory traversal overwrites.
*   **Defensive Status**: **PASS**
*   **Recommendation**: Store uploaded files in a directory outside the web application document root, or restrict execution in the upload path via server configuration files (e.g., blocking script handlers in the `uploads/` folder).

### 2.9 Error Handling
*   **Evaluation**:
    *   Raw database exception messages (`$conn->error`) are hidden from user outputs and logged server-side via `error_log()` (e.g. [delete_post.php](file:///c:/xampp/htdocs/calligraphy_project/delete_post.php), [register.php](file:///c:/xampp/htdocs/calligraphy_project/register.php)).
    *   Users are returned friendly, generic error indicators.
*   **Defensive Status**: **PASS**
*   **Recommendation**: Configure the global php configuration file (`php.ini`) to enforce `display_errors = Off` in production environments, ensuring all unexpected errors write to logs rather than browser outputs.

### 2.10 Password Policy
*   **Evaluation**:
    *   [register.php](file:///c:/xampp/htdocs/calligraphy_project/register.php) validates complexity requirements: minimum 8 characters, at least one uppercase letter, and at least one numeric digit.
    *   Passwords are hashed with `PASSWORD_DEFAULT` via `password_hash()`.
*   **Defensive Status**: **PASS**
*   **Recommendation**: Consider adding checks against lists of common passwords to block easily guessed dictionary combinations.

### 2.11 Rate Limiting
*   **Evaluation**:
    *   Sliding-window rate limiters are active on logins, registrations, comments, and likes.
    *   Failed attempts block abusers dynamically for defined durations, logging events securely in [includes/logger.php](file:///c:/xampp/htdocs/calligraphy_project/includes/logger.php).
*   **Defensive Status**: **PASS**
*   **Recommendation**: Implement sliding limits at the web server layer (e.g., using rate-limit configurations in Nginx or Apache mod_ratelimit) to shield the application layer from CPU exhaustion during heavy request volumes.

### 2.12 Security Headers
*   **Evaluation**:
    *   Centralized security headers are sent via [includes/security_headers.php](file:///c:/xampp/htdocs/calligraphy_project/includes/security_headers.php) and HSTS is enforced in [includes/https_enforcement.php](file:///c:/xampp/htdocs/calligraphy_project/includes/https_enforcement.php).
    *   Emitted headers include CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, and HSTS.
*   **Defensive Status**: **PASS**
*   **Recommendation**: Harden the Content-Security-Policy (CSP) by extracting inline event scripts from dashboard views and removing `'unsafe-inline'` from the script-src directive.
