# CSRF Remediation Report

This report documents the changes made to introduce a system-wide Cross-Site Request Forgery (CSRF) protection layer in Calligraphy Central.

---

## 1. Summary of Actions

We created a centralized CSRF protection module, updated all state-modifying forms to include hidden session-tied tokens, secured all state-changing endpoints, and converted critical database actions (such as deletion) from unsafe GET parameters to protected POST requests.

---

## 2. Files Modified

| File Name | Change Category | Description |
| :--- | :--- | :--- |
| **`includes/csrf.php`** | [NEW] | Core module providing `generateCSRFToken()` and `verifyCSRFToken()`. |
| **`delete_post.php`** | [MODIFY] | Converted request parser to expect POST instead of GET parameters. Added `verifyCSRFToken()` validation check. |
| **`gallery.php`** | [MODIFY] | Included `csrf.php`. Converted Admin DELETE anchor link to a POST form button. Embedded CSRF token into comment forms and like submission forms. |
| **`my_posts.php`** | [MODIFY] | Included `csrf.php`. Converted owner DELETE anchor link to a POST form button. |
| **`admin_dashboard.php`** | [MODIFY] | Included `csrf.php`. Converted Admin DELETE anchor link to a POST form button. |
| **`upload.php`** | [MODIFY] | Included `csrf.php`. Embedded token inside upload form, and verified it in standard upload processing block. |
| **`edit_posts.php`** | [MODIFY] | Included `csrf.php`. Embedded token inside edit form, and verified it in update processing block. |
| **`view_post.php`** | [MODIFY] | Included `csrf.php`. Added hidden token fields to the like and comment submission forms. |
| **`submit_comments.php`** | [MODIFY] | Included `csrf.php`. Verified CSRF token before comments insert queries. |
| **`like_posts.php`** | [MODIFY] | Included `csrf.php`. Verified CSRF token before likes inserts or deletes. |
| **`register.php`** | [MODIFY] | Included `csrf.php`. Added token verification on sign-up POST request and hidden input field in form. |
| **`login.php`** | [MODIFY] | Included `csrf.php`. Added token verification on login POST request and hidden input field in form. |

---

## 3. Form and Endpoint Protection Inventory

### 3.1 Forms Updated with `<input type="hidden" name="csrf_token" ...>`
1.  **Sign Up Form** (`register.php`)
2.  **Login Form** (`login.php`)
3.  **Post Gallery Form** (`upload.php`)
4.  **Edit Post Form** (`edit_posts.php`)
5.  **Submit Comment Form** (`view_post.php`)
6.  **Like / Unlike Button Forms** (`gallery.php` and `view_post.php`)
7.  **Admin Delete Post Form** (`gallery.php`)
8.  **Owner Delete Post Form** (`my_posts.php`)
9.  **Dashboard Delete Post Form** (`admin_dashboard.php`)

### 3.2 Endpoints Protected
All state-modifying POST requests are validated at the database interface tier:
*   `register.php` (blocks registration spoofing)
*   `login.php` (secures login submissions)
*   `upload.php` (verifies uploader credentials)
*   `edit_posts.php` (secures updates to captions/media)
*   `submit_comments.php` (blocks spam comments)
*   `like_posts.php` (protects likes manipulation)
*   `delete_post.php` (prevents unauthorized deletions)

---

## 4. GET Actions Converted to POST

### Endpoint: `delete_post.php`
*   **Previous Implementation**: Accessed using GET queries (`delete_post.php?id=[post_id]`). This setup was highly vulnerable, allowing attackers to delete posts simply by tricking authenticated users (especially admins) into visiting a crafted URL.
*   **New Implementation**: Accepts only POST requests. The action checks for a valid post ID parameter via `$_POST['id']` and validates it against `verifyCSRFToken()`.
*   **Client Updates**: All delete links (in the gallery feed, the user portfolio, and the admin dashboard) were converted to POST forms containing the post ID and the CSRF token. The buttons were styled to look exactly like the legacy buttons.

---

## 5. Remaining Security Concerns

While CSRF and RCE on upload are fully resolved, the following issues should be addressed in subsequent remediation phases:
1.  **Lack of HTTPS/TLS Enforcements**: Session cookies do not possess `Secure` flags, allowing session interception over insecure networks.
2.  **Missing Security Headers**: The application does not specify security-hardening headers such as `Content-Security-Policy` (CSP) or `X-Frame-Options` (remediation for clickjacking).
3.  **Raw Input in Database (Stored XSS Risk)**: Comments and captions are saved as raw values. If any future page renders these records without passing them through `htmlspecialchars()`, Stored XSS will execute.
4.  **No Rate-Limiting**: The authentication endpoints (`login.php`, `register.php`) and write actions (`submit_comments.php`) do not enforce request rate-limiting, leaving them vulnerable to automated brute-force attacks.
