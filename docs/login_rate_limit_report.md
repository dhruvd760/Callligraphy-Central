# Login Rate Limiting & Brute-Force Protection Report

This report documents the security controls implemented to protect the user authentication interface (`login.php`) against automated password brute-force and credential stuffing attacks.

---

## 1. Executive Summary

We have implemented a hybrid brute-force protection system for Calligraphy Central. It integrates a database-backed log of failed login attempts for precise IP-address and email tracking, and uses a session-based backup to ensure continuous defense even if the database is temporarily read-only or undergoing maintenance. 

---

## 2. Hardening Measures Implemented

### 2.1 Centralized Protection Module
Created a reusable authentication rate limiter at [includes/login_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/login_rate_limit.php) that exposes:
*   `checkLoginRateLimit($conn, $email)`: Resolves if the requester is currently locked out.
*   `recordFailedLoginAttempt($conn, $email)`: Logs failed attempts and increments counters.
*   `clearLoginAttempts($conn, $email)`: Flushes historical attempts upon successful verification.

### 2.2 Rate Limit Policies & Scope
*   **Threshold**: Maximum of **5 failed attempts** are permitted.
*   **Lockout Window**: **15 minutes** (900 seconds) lockout duration.
*   **Scoped Tracking**: Monitored simultaneously by client IP address (`$_SERVER['REMOTE_ADDR']`) and input email address. This prevents attackers from bypassing IP restrictions via simple proxy rotation (by locking the target account) and blocks distributed attacks targeting single accounts.
*   **Pruning**: Automatically deletes expired attempt logs older than 15 minutes before counting failures to ensure a sliding window lockout.

### 2.3 Defensive Logging
*   All failed login attempts are written to the server's error log via `error_log()` including the attempted email and IP address.
*   Lockout triggers write a high-priority log entry: `error_log("Suspicious activity: Login lockout triggered for email '$email' from IP '$ip_address' (Attempts: $count)")`.

### 2.4 Resilient Session Fallback
If the database connection is interrupted or the user does not possess write privileges for the `login_attempts` table, the system handles the exception gracefully by falling back to session-based rate-limiting (`$_SESSION['failed_attempts']` and `$_SESSION['lockout_time']`).

---

## 3. Audited and Modified Files

| File Name | Security Change Description |
| :--- | :--- |
| **[includes/login_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/login_rate_limit.php)** | [NEW] Primary logic engine handling dynamic table setup, failed attempt logging, and sliding lockout computations. |
| **[login.php](file:///c:/xampp/htdocs/calligraphy_project/login.php)** | [MODIFY] Integrated rate limiting checks immediately after CSRF validation. Hooks success/failure routes to log and reset controls. |

---

## 4. Verification and Functional Compatibility

*   **Syntax Integrity**: Confirmed all files compile without syntax errors via `php -l`.
*   **Redirection & Session Preservation**: Successful authentication still triggers proper session regeneration and correctly logs users into the gallery board, preserving backward compatibility.
*   **User Feedback**: Locked-out users receive a clean user-friendly alert message: `Too many failed login attempts. Please try again in X minute(s).`
