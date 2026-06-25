# Registration Rate Limiting & Abuse Prevention Report

This report documents the security controls implemented to protect the user registration interface (`register.php`) against automated spam accounts, dictionary registration, and database flooding.

---

## 1. Executive Summary

We have implemented a system-wide registration rate-limiting control. It uses a database-backed log of registration attempts to restrict rapid account creation from a single client IP address, and uses a session-based backup to guarantee lockout enforcement even in database-restricted contexts.

---

## 2. Hardening Measures Implemented

### 2.1 Centralized Protection Module
Created a reusable registration rate limiter at [includes/register_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/register_rate_limit.php) that exposes:
*   `checkRegisterRateLimit($conn)`: Resolves if the requester's IP address has exceeded registration limits.
*   `recordRegistrationAttempt($conn)`: Logs registration attempts and increments lockout counters.

### 2.2 Rate Limit Policies & Scope
*   **Threshold**: Maximum of **5 registration attempts** are permitted.
*   **Lockout Window**: **1 hour** (3600 seconds) lockout duration.
*   **Scoped Tracking**: Monitored strictly by client IP address (`$_SERVER['REMOTE_ADDR']`). This stops bots from generating dozens of mock profiles even if they vary user names, passwords, and email patterns.
*   **Pruning**: Automatically deletes expired attempt logs older than 1 hour before counting registration attempts to ensure a sliding window lockout.

### 2.3 Defensive Logging
*   All registration attempts are logged: `error_log("Registration attempt from IP '$ip_address'")`.
*   Lockout triggers write a high-priority log entry: `error_log("Suspicious activity: Registration lockout triggered for IP '$ip_address' (Attempts: $count)")`.

### 2.4 Resilient Session Fallback
If the database connection is interrupted or the user does not possess write privileges for the `registration_attempts` table, the system handles the exception gracefully by falling back to session-based rate-limiting (`$_SESSION['register_attempts']` and `$_SESSION['register_lockout_time']`).

---

## 3. Audited and Modified Files

| File Name | Security Change Description |
| :--- | :--- |
| **[includes/register_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/register_rate_limit.php)** | [NEW] Primary rate limit logic handler checking sliding-window limits, updating DB tables, and managing session fallbacks. |
| **[register.php](file:///c:/xampp/htdocs/calligraphy_project/register.php)** | [MODIFY] Integrated rate limiting checks immediately after CSRF verification. Hooks attempt submissions to the rate-limiter recorder. |

---

## 4. Verification and Functional Compatibility

*   **Syntax Integrity**: Confirmed all files compile without syntax errors via `php -l`.
*   **User Experience**: Genuine users registering normally are not disrupted. If an IP exceeds the attempt threshold, they receive a clean user-friendly alert message: `Too many registration attempts. Please try again in X minute(s).`
