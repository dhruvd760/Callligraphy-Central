# Comment Rate Limiting & Spam Protection Report

This report documents the security controls implemented to protect the comment submission flow (`submit_comments.php`) against automated spam, comment flooding, and database overload.

---

## 1. Executive Summary

We have implemented a robust rate-limiting control for comment submissions. It limits the frequency at which authenticated users can submit comments on the application, tracking requests via a database log with an active session-based backup to ensure failure-resiliency.

---

## 2. Hardening Measures Implemented

### 2.1 Centralized Protection Module
Created a reusable comment rate limiter at [includes/comment_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/comment_rate_limit.php) that exposes:
*   `checkCommentRateLimit($conn, $user_id)`: Resolves if the user has exceeded comment frequency limits.
*   `recordCommentAttempt($conn, $user_id)`: Records the timestamp of comment attempts.

### 2.2 Rate Limit Policies & Scope
*   **Threshold**: Maximum of **5 comment submissions** are permitted.
*   **Time Window**: Sliding window of **60 seconds** (1 minute).
*   **Scoped Tracking**: Monitored by the user's authenticated account `user_id` (since commenting requires a valid logged-in session).
*   **Pruning**: Automatically deletes expired attempt logs older than 60 seconds before checking comment limits to maintain sliding-window accuracy.

### 2.3 Defensive Logging
*   All comment rate-limit blocks are logged to the server error log: `error_log("Suspicious activity: Comment rate limit exceeded for User ID '$user_id'")`.

### 2.4 Resilient Session Fallback
If the database connection is interrupted or the user does not possess write privileges for the `comment_attempts` table, the system handles the exception gracefully by falling back to session-based rate-limiting (`$_SESSION['comment_attempts']` array).

---

## 3. Audited and Modified Files

| File Name | Security Change Description |
| :--- | :--- |
| **[includes/comment_rate_limit.php](file:///c:/xampp/htdocs/calligraphy_project/includes/comment_rate_limit.php)** | [NEW] Centralized rate limiter checking sliding window timestamps in DB/sessions and writing attempt logs. |
| **[submit_comments.php](file:///c:/xampp/htdocs/calligraphy_project/submit_comments.php)** | [MODIFY] Integrated rate limiting checks immediately after CSRF validation. Redirects blocked users back to the post page with an error status. |
| **[view_post.php](file:///c:/xampp/htdocs/calligraphy_project/view_post.php)** | [MODIFY] Render warning banner above inline comment submission form if the request context contains the rate limit error query parameter. |

---

## 4. Verification and Functional Compatibility

*   **Syntax Integrity**: Confirmed all files compile without syntax errors via `php -l`.
*   **User Interface Compatibility**: Renders a user-friendly error message alert banner above the comment input field when a user is locked out: `You are posting comments too fast. Please wait a moment before trying again.` Normal users post comments without any change in user experience.
