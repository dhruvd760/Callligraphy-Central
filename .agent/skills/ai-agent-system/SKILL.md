---
name: "AI Agent System Specialist"
description: "Orchestrates execution, safety bounds, and Python interfaces for autonomous LLMs."
---

### Interaction Guidelines
*   **Boundary Enforcement**: Python agent components must run in isolation under `/python_ai/` and `/agents/`.
*   **State Recording**: Write logs and model history runs to `/memory/` for tracking execution metrics.
*   **API Integrity**: Restrict agent interface to designated endpoint handlers under `/api/`.
