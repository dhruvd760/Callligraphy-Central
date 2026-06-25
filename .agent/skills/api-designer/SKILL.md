---
name: "API Designer"
description: "Creating and structuring REST endpoints under the api/ folder."
---

### API Rules
*   **Directory Routing**: Endpoint entry points reside in `/api/`.
*   **Response Payload**: Returns application/json header with keys `status`, `message`, and `data`.
*   **Method Restrictions**: Enforce appropriate HTTP verbs (GET for fetching feed, POST for updating state).
