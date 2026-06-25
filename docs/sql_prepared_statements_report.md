# SQL Prepared Statements and Query Audit Report

This report documents the security corrections and type-alignment adjustments applied to the database query logic of Calligraphy Central.

---

## 1. Summary of Database Query Audits

A review was conducted of all files containing database interactions (such as `query()` or `prepare()` execution calls). Although input parameters inside `view_post.php` were sanitized using `intval()`, they were still interpolated directly into raw query strings, which deviates from secure parameterization invariants. Additionally, a type binding mismatch was identified in `my_posts.php`.

---

## 2. Parameterization and Alignment Fixes

### 2.1 File: `view_post.php` (Post Retrieval Query)
*   **Vulnerability Profile**: Raw SQL query with dynamic variable interpolation.
*   **Root Cause**: The `$post_id` variable was concatenated directly inside the SELECT statement.
*   **Correction**: Converted the query to a prepared statement and bound the parameter with integer typing (`"i"`):
    *   *Before*:
        ```php
        $sql = "SELECT ... WHERE posts.post_id = $post_id";
        $result = $conn->query($sql);
        ```
    *   *After*:
        ```php
        $sql = "SELECT ... WHERE posts.post_id = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("i", $post_id);
        $stmt->execute();
        $result = $stmt->get_result();
        ```

### 2.2 File: `view_post.php` (Comments Thread Query)
*   **Vulnerability Profile**: Raw SQL query with dynamic variable interpolation.
*   **Root Cause**: The `$post_id` variable was concatenated directly inside the comment selection statement.
*   **Correction**: Converted the comments select query to a prepared statement and bound the parameter with integer typing (`"i"`):
    *   *Before*:
        ```php
        $comments_sql = "SELECT ... WHERE c.post_id = $post_id ORDER BY ...";
        $comments_result = $conn->query($comments_sql);
        ```
    *   *After*:
        ```php
        $comments_sql = "SELECT ... WHERE c.post_id = ? ORDER BY ...";
        $c_stmt = $conn->prepare($comments_sql);
        $c_stmt->bind_param("i", $post_id);
        $c_stmt->execute();
        $comments_result = $c_stmt->get_result();
        ```

### 2.3 File: `my_posts.php` (User ID Parameter Binding)
*   **Vulnerability Profile**: Type mismatch in parameter binding.
*   **Root Cause**: The `$current_user` integer (corresponding to `user_id`) was bound as a string placeholder (`"s"`).
*   **Correction**: Changed the parameter binding format placeholder to integer typing (`"i"`):
    *   *Before*:
        ```php
        $stmt->bind_param("s", $current_user);
        ```
    *   *After*:
        ```php
        $stmt->bind_param("i", $current_user);
        ```

---

## 3. Static Query Verification
The remaining direct `query()` calls in the application are verified to be strictly static. They contain no dynamic input parameters or interpolated variables, making them secure against injection:
1.  **`admin_dashboard.php` (line 21)**:
    `$conn->query("SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.user_id ORDER BY upload_date DESC");`
2.  **`gallery.php` (line 23)**:
    `$conn->query($sql);` (where `$sql` is a hardcoded query string representing the global posts feed join).
