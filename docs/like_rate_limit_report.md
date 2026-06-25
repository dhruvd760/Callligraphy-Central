# Post Likes Rate Limiting & Abuse Prevention Report

This report documents the security controls implemented to protect the post liking/unliking action flow (`like_posts.php`) against automated likes manipulation and rapid database flooding.

---

## 1. Executive Summary

We have implemented a system-wide post likes rate-limiting control. It monitors the frequency of like/unlike activities per user, logging requests via a database log with an active session-based fallback to guarantee continuous security.

---

## 2. Hardening Measures Implemented

### 2.1 Centralized Protection Module
Created a reusable likes rate limiter at [includes/like_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/like_rate_limit.php) that exposes:
*   `checkLikeRateLimit($conn, $user_id)`: Resolves if the user has exceeded liking limits.
*   `recordLikeAttempt($conn, $user_id)`: Records the timestamp of likes attempts.

### 2.2 Rate Limit Policies & Scope
*   **Threshold**: Maximum of **10 likes/unlikes attempts** are permitted.
*   **Time Window**: Sliding window of **30 seconds**.
*   **Scoped Tracking**: Monitored by the user's authenticated account `user_id` (since liking posts requires a valid logged-in session).
*   **Pruning**: Automatically deletes expired attempt logs older than 30 seconds before checking limits to maintain sliding-window accuracy.

### 2.3 Defensive Logging & Silent Drop
*   All blocked actions are written to the server's error log: `error_log("Suspicious activity: Like rate limit exceeded for User ID '$user_id'")`.
*   To preserve the existing visual continuity and functionality without introducing complex UI popups, when rate limits are triggered the attempt is logged and the client is immediately redirected back to the referring page without updating the likes pivot table.

### 2.4 Resilient Session Fallback
If the database connection is interrupted or the user does not possess write privileges for the `like_attempts` table, the system handles the exception gracefully by falling back to session-based rate-limiting (`$_SESSION['like_attempts']` array).

---

## 3. Audited and Modified Files

| File Name | Security Change Description |
| :--- | :--- |
| **[includes/like_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/like_rate_limit.php)** | [NEW] Centralized rate limiter checking sliding window timestamps in DB/sessions and writing attempt logs. |
| **[like_posts.php](file:///c:/xampp/htdocs/calligraphy_project/like_posts.php)** | [MODIFY] Integrated rate limiting checks immediately after CSRF validation. Redirects blocked users back to the post/gallery page without making changes. |

---

## 4. Verification and Functional Compatibility

*   **Syntax Integrity**: Confirmed all files compile without syntax errors via `php -l`.
*   **Functional Compatibility**: Normal users liking artwork occasionally are not restricted. Attackers using rapid script triggers are silently blocked and logged.
