# Stored XSS Audit and Remediation Report

This report documents the security fixes applied to Calligraphy Central to prevent Stored Cross-Site Scripting (XSS) and HTML Attribute Injection.

---

## 1. Remediation Scope

We audited all locations in the user-facing and administrator controllers that output database values or client-supplied inputs. We updated these outputs to explicitly call `htmlspecialchars($value, ENT_QUOTES, 'UTF-8')`. Values inside SQL queries were untouched to prevent query corruption, ensuring that sanitization remains strictly at the output presentation tier.

---

## 2. Remediated Locations and Variables

### 2.1 File: `admin_dashboard.php`
*   **Vulnerability Fixed**: Raw file names were injected directly inside `src` attributes of video and image elements inside the admin loop.
*   **Variables remediated**:
    *   `$row['file_name']` (escaped as `$escaped_file_name` inside `<video src="...">` and `<img src="...">`).
    *   `$row['post_id']` (escaped inside hidden form fields).
    *   `$row['title']` (escaped in title column).
    *   `$row['username']` (escaped in uploader column).

### 2.2 File: `gallery.php`
*   **Vulnerability Fixed**: General output fields lacked strict encoding parameters.
*   **Variables remediated**:
    *   `$row['post_id']` (escaped inside card IDs, anchor links, and hidden inputs).
    *   `$row['file_name']` (escaped inside image `src` and video source `src` attributes).
    *   `$row['file_type']` (escaped inside video `type` attributes).
    *   `$row['username']` (escaped in author displays).
    *   `$row['like_count']` (escaped inside interaction metrics).
    *   `$row['title']` and `$row['description']` (escaped in text headers and captions).

### 2.3 File: `view_post.php`
*   **Vulnerability Fixed**: Raw metadata rendered inside video and share links was exposed.
*   **Variables remediated**:
    *   `$post['file_name']` (escaped inside media tags).
    *   `$post['username']` (escaped in card header).
    *   `$post['post_id']` (escaped inside hidden inputs, like forms, and within share input text).
    *   `$post['like_count']` (escaped inside count badge).
    *   `$_SERVER['HTTP_HOST']` (escaped inside the generated share URL input).
    *   `dirname($_SERVER['PHP_SELF'])` (escaped inside share URL input).
    *   `$post['title']` and `$post['description']` (escaped in captions).
    *   `$c_row['username']` and `$c_row['comment_text']` (escaped in comments list).

### 2.4 File: `my_posts.php`
*   **Vulnerability Fixed**: Dynamic elements printed inside PHP `echo` statement strings bypassed strict encoding context flags.
*   **Variables remediated**:
    *   `$row['file_name']` (escaped inside media blocks).
    *   `$row['file_type']` (escaped inside video source attributes).
    *   `$row['username']` (escaped in username tag).
    *   `$row['title']` (escaped in header titles).
    *   `$row['post_id']` (escaped in edit links and forms).
    *   `$row['description']` (escaped in caption outputs).

---

## 3. Verification & Compliance
*   **No Code Injection**: All sanitizations are executed during output generation (`View` level). Database persistence continues to save raw values as submitted by the user.
*   **Syntax Integrity**: Confirmed by local compiler analysis. All pages execute normally without warnings.
