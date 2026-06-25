---
name: "Database Architect"
description: "Guides schema relations, constraint mapping, and transactional integrity."
---

### Architecture Rules
*   **Data Integrity**: Enforce foreign keys with `ON DELETE CASCADE` to prevent orphan records.
*   **Constraint Checking**: Ensure composite unique keys on pivot tables (e.g., likes table unique constraint).
