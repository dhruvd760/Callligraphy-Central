---
name: "PHP Backend Engineer"
description: "Guidelines for writing, managing, and updating procedural PHP pages."
---

### Development Guidelines
*   **Page Controller Pattern**: Keep request handling at the top and HTML rendering at the bottom.
*   **Database Connections**: Always reference `includes/db_connect.php` to obtain the `$conn` connection context.
*   **Session Initialization**: Use `session_start()` at the absolute beginning of script executables requiring user verification.
*   **Data Validation**: Sanitize inputs and enforce structural constraints (e.g., character length limit of 400 on captions).
