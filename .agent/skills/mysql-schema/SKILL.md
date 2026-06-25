---
name: "MySQL Schema Manager"
description: "Handling tables, fields, constraints, and relational integrity in calligraphy_db."
---

### Database Guidelines
*   **Schema Target**: Database `calligraphy_db` with tables `users`, `posts`, `likes`, and `comments`.
*   **Relational Integrity**: Maintain foreign keys linking tables back to `users` and `posts` with `ON DELETE CASCADE`.
*   **Prepared Statements**: Bind user parameters using MySQLi prepared statements to eliminate SQL injection threat.
