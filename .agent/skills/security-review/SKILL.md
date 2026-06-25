---
name: "Security Review Auditor"
description: "Rules and checklists for identifying and patching vulnerabilities."
---

### Security Auditing Rules
*   **SQL Injection**: Ensure query inputs are parameterized (prepared statements).
*   **Cross-Site Scripting (XSS)**: Escape all outputs containing user data on client pages using `htmlspecialchars()`.
*   **Media Security**: Validate uploaded file extensions to prevent executing binary payloads or server scripts in `uploads/`.
