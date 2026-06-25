---
name: "Performance Optimizer"
description: "Maximizing rendering speed and query execution times."
---

### Optimization Rules
*   **Query Indexing**: Verify that foreign keys are indexed for faster joins.
*   **Caching Controls**: Implement caching limits on static media files, but enforce anti-caching headers on dynamic forms.
*   **Payload Minimization**: Optimize SQL selects (avoiding `SELECT *` where possible).
