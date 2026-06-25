# Code Quality Audit Report

This report documents the code quality, duplication, validation inconsistencies, include structures, and architectural debt within the **Calligraphy Central** application, providing actionable, defensive refactoring recommendations.

---

## 1. Identified Code Duplication

Procedural coding patterns have introduced several blocks of duplicated logic across page scripts:

### 1.1 Media Rendering Selector
*   **Duplicate Blocks**:
    *   [gallery.php](file:///c:/xampp/htdocs/calligraphy_project/gallery.php) (Lines 32–42)
    *   [my_posts.php](file:///c:/xampp/htdocs/calligraphy_project/my_posts.php) (Lines 38–46)
    *   [view_post.php](file:///c:/xampp/htdocs/calligraphy_project/view_post.php) (Lines 40–45)
    *   [admin_dashboard.php](file:///c:/xampp/htdocs/calligraphy_project/admin_dashboard.php) (Lines 33–34)
*   **Mechanism**: The code checks the database field `file_type` (using `strpos` or `str_starts_with` to see if it starts with/contains `'image'`) and decides whether to output an `<img>` tag or a `<video>` block.
*   **Maintenance Impact**: If a new media player library or formatting layout is introduced, developers must update four separate files, increasing the risk of visual inconsistencies.

### 1.2 Authentication Guards
*   **Duplicate Blocks**:
    *   [upload.php](file:///c:/xampp/htdocs/calligraphy_project/upload.php) (Lines 7–13)
    *   [delete_post.php](file:///c:/xampp/htdocs/calligraphy_project/delete_post.php) (Lines 7–13)
    *   [edit_posts.php](file:///c:/xampp/htdocs/calligraphy_project/edit_posts.php) (Lines 7–13)
    *   [like_posts.php](file:///c:/xampp/htdocs/calligraphy_project/like_posts.php) (Lines 7–11)
    *   [submit_comments.php](file:///c:/xampp/htdocs/calligraphy_project/submit_comments.php) (Lines 7–12)
    *   [my_posts.php](file:///c:/xampp/htdocs/calligraphy_project/my_posts.php) (Lines 7–11)
*   **Mechanism**: Each action script manually checks `!isset($_SESSION['user_id'])`, logs the violation, and redirects to `login.php`.
*   **Maintenance Impact**: Redundant logic. Centralizing this check makes the routing lifecycle easier to manage.

---

## 2. Detected Dead Code

We identified the following orphaned scripts and dead code statements:

### 2.1 Commented-out Code Drafts
*   **Location**: [login.php](file:///c:/xampp/htdocs/calligraphy_project/login.php)
    *   Line 34: Commented-out query execution syntax (`$result = $conn->execute_query(...)`).
    *   Line 61: Commented-out query resource closing statement (`$stmt->close();`).
*   **Maintenance Impact**: Increases visual clutter and can confuse future developers.

### 2.2 Orphaned View Pages
*   **Location**: [getting-started.php](file:///c:/xampp/htdocs/calligraphy_project/getting-started.php)
*   **Mechanism**: The link to `getting-started.php` in [includes/header.php](file:///c:/xampp/htdocs/calligraphy_project/includes/header.php) is commented out:
    ```html
    <!-- <li class="mob"><a href="getting-started.php">Getting Started</a></li> -->
    ```
    However, the physical script [getting-started.php](file:///c:/xampp/htdocs/calligraphy_project/getting-started.php) still exists in the root folder.
*   **Maintenance Impact**: Creates a dead route that is inaccessible through normal user navigation, but remains accessible to crawlers.

---

## 3. Detected Inconsistent Validation

### 3.1 Comment Length Validation
*   **Location**: [submit_comments.php](file:///c:/xampp/htdocs/calligraphy_project/submit_comments.php)
*   **Inconsistency**: The script trims and verifies that the comment is not empty, but it does not check the maximum length of the comment. A malicious request can post a multi-megabyte comment block, leading to database resource bloat.

### 3.2 Key Integrity checks
*   **Location**: [like_posts.php](file:///c:/xampp/htdocs/calligraphy_project/like_posts.php)
*   **Inconsistency**: Unlike the post edit page which verifies that the target `post_id` exists in the database, `like_posts.php` immediately attempts database insertion/deletion of the like using the provided ID without verifying that the post exists, relying solely on foreign key checks in the database.

---

## 4. Include Structure Review

*   **Current State**:
    *   Files use a mixture of `include` and `include_once` (e.g., `include 'includes/db_connect.php';` and `include_once 'includes/session_config.php';`).
*   **Analysis**:
    *   `include` only triggers a warning (E_WARNING) if a file is missing, and execution continues. If a critical helper (like `db_connect.php` or `csrf.php`) is missing, subsequent logic will fail, potentially exposing uninitialized variables.
    *   `require_once` stops execution with a fatal error (E_COMPILE_ERROR) if the target file cannot be loaded, which is much safer for core dependencies.

---

## 5. Architectural & Maintainability Debt

*   **High Coupling**: Visual HTML outputs, database operations, business validation checks, and route redirections are combined in single files.
*   **Redirect Warnings**: HTML headers in [includes/header.php](file:///c:/xampp/htdocs/calligraphy_project/includes/header.php) are included before POST processing operations complete (e.g. in `register.php`), which can result in PHP "headers already sent" warnings if output buffering is disabled in php configurations.

---

## 6. Recommended Refactoring Opportunities

To address these code quality issues, we recommend the following refactoring steps:

### 6.1 Centralize Media Rendering
Create a shared visual helper inside [includes/header.php](file:///c:/xampp/htdocs/calligraphy_project/includes/header.php) or a new `includes/media_helper.php`:
```php
function renderMediaElement($file_name, $file_type, $styles = "") {
    $escaped_name = htmlspecialchars($file_name, ENT_QUOTES, 'UTF-8');
    $escaped_type = htmlspecialchars($file_type, ENT_QUOTES, 'UTF-8');
    
    if (strpos($file_type, 'image') !== false) {
        return "<img src='uploads/{$escaped_name}' alt='Artwork' style='{$styles}'>";
    } else {
        return "<video controls style='{$styles}'><source src='uploads/{$escaped_name}' type='{$escaped_type}'></video>";
    }
}
```

### 6.2 Standardize Authentication Guards
Centralize authentication checks into a reusable function inside [includes/session_config.php](file:///c:/xampp/htdocs/calligraphy_project/includes/session_config.php):
```php
function enforceAuthentication($log_message = "Unauthorized access attempt") {
    if (!isset($_SESSION['user_id'])) {
        writeSecurityLog('unauthorized_access', $log_message);
        header("Location: login.php");
        exit();
    }
}
```

### 6.3 Standardize Dependency Inclusions
Replace loose `include` configurations with `require_once` for all critical logic dependencies (e.g. database connect, rate limiting, and configurations).
```php
// Before
include 'includes/db_connect.php';

// After
require_once __DIR__ . '/includes/db_connect.php';
```
