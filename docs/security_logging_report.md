# Centralized Security Logging Report

This report documents the security logger utility and the integration of log event hooks across the application to trace security failures and unauthorized attempts.

---

## 1. Executive Summary

We have integrated a centralized security logging engine for Calligraphy Central. It stores critical security events in an isolated file on the filesystem with active directory protection and data redaction policies to prevent credential leakage.

---

## 2. Hardening Measures Implemented

### 2.1 Centralized Logging Utility
Created a centralized logging helper at [includes/logger.php](file:///c:/xampp/htdocs/calligraphy_project/includes/logger.php) which defines:
*   `writeSecurityLog($event_type, $message, $metadata)`: Sanitizes metadata, formats log entries, writes to `logs/security.log`, and mirrors to PHP's standard error logger.

### 2.2 Directory Protections
*   **Log Storage**: Logs are written to `logs/security.log`.
*   **Web Access Denied**: A `.htaccess` file containing `Deny from all` is automatically created inside the `logs/` directory to prevent attackers from viewing or downloading log contents directly via the browser.

### 2.3 Information Redaction
To prevent sensitive user information (such as credentials or tokens) from being stored in plain text on the server, the logging utility automatically filters incoming metadata arrays. Any keys matching sensitive patterns (such as `password`, `csrf`, `token`, `secret`) are replaced with `[REDACTED]`.

---

## 3. Log Event Catalog

The logging hooks are integrated at all major security execution boundaries:

| Event Type | File Hook Location | Description |
| :--- | :--- | :--- |
| **`failed_login`** | [includes/login_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/login_rate_limit.php) | Triggered when credential match validation fails on the login form. |
| **`invalid_csrf`** | [includes/csrf.php](file:///c:/xampp/htdocs/calligraphy_project/includes/csrf.php) | Triggered when verifyCSRFToken fails due to missing or invalid token parameters. |
| **`unauthorized_access`** | [admin_dashboard.php](file:///c:/xampp/htdocs/calligraphy_project/admin_dashboard.php), [edit_posts.php](file:///c:/xampp/htdocs/calligraphy_project/edit_posts.php), [delete_post.php](file:///c:/xampp/htdocs/calligraphy_project/delete_post.php), [upload.php](file:///c:/xampp/htdocs/calligraphy_project/upload.php), [submit_comments.php](file:///c:/xampp/htdocs/calligraphy_project/submit_comments.php), [like_posts.php](file:///c:/xampp/htdocs/calligraphy_project/like_posts.php) | Triggered when guest users request access to restricted controllers, or when standard users attempt admin dashboard access / unauthorized post deletion. |
| **`upload_validation_failed`** | [upload.php](file:///c:/xampp/htdocs/calligraphy_project/upload.php), [edit_posts.php](file:///c:/xampp/htdocs/calligraphy_project/edit_posts.php) | Triggered when payload sizes exceed constraints, extensions fail validation checks, or files exceed configuration limits. |
| **`suspicious_activity`** | [includes/login_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/login_rate_limit.php), [includes/register_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/register_rate_limit.php), [includes/comment_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/comment_rate_limit.php), [includes/like_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/like_rate_limit.php) | Triggered when sliding-window rate limit counters exceed thresholds and activate lockouts. Also logged if file moves fail. |

---

## 4. Verification and Functional Compatibility

*   **Syntax Integrity**: Confirmed all files compile without syntax errors via `php -l`.
*   **Format**: Log entries are formatted as:
    `[Timestamp] [SECURITY] [Event: EVENT_TYPE] [IP: Client_IP] [User ID: Current_User] - Message | Metadata: {JSON}`
*   **Web Protection**: Direct browser access to `logs/security.log` is securely blocked with a `403 Forbidden` response.
