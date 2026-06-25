---
name: "Migration Manager"
description: "Managing schema version changes and script updates safely."
---

### Migration Rules
*   Write incremental delta scripts instead of rewriting the base `database.sql`.
*   Maintain database schema integrity during live migrations.
