# Calligraphy Central - Capstone Requirements Compliance

This document maps Calligraphy Central's preparation steps to the rules and goals of the **Google × Kaggle Agentic AI Capstone**.

---

## 1. Capstone Context

The Google × Kaggle Agentic AI Capstone requires building autonomous agent systems capable of working within existing software applications. Instead of rebuilding code from scratch, the agents must interact with a legacy codebase to perform diagnostics, audits, testing, security remediation, and API generation.

### Key Evaluation Drivers
1.  **Safety & Security**: Preventing vulnerabilities (SQLi, XSS, CSRF, insecure uploads) during changes.
2.  **Compatibility Integrity**: Guaranteeing that legacy application code runs unmodified and functions exactly as expected for normal clients.
3.  **Agentic Capabilities**: Demonstrating how autonomous subagents can leverage specialised files (skills) to execute actions.
4.  **Token & Prompt Efficiency**: Running agentic pipelines without excessive context bloat or infinite tool loops.

---

## 2. Preparation Phase Checklist

To comply with the capstone's environment setup:
*   [x] **Project Constitution**: Establish a supreme law document (`PROJECT_CONSTITUTION.md`) to constrain agent tasks.
*   [x] **Project Specification**: Detail legacy functionalities (`PROJECT_SPEC.md`) so agents have clear behavioral references.
*   [x] **System Architecture**: Describe page flows and database models (`ARCHITECTURE.md`) to prevent architectural degradation.
*   [x] **Agent Skills Directory**: Build `.agent/skills/` to provide immediate, fine-grained domain constraints for models.
*   [x] **Supporting Directories**: Establish clear folder boundaries to isolate new modules from the legacy website root (`agents/`, `memory/`, `python_ai/`, `api/`, `evaluation/`, `competition/`, `docs/`, `assets/`).

---

## 3. Future Competition Deliverables

When submitting the final Capstone project, the agentic system must package the following items into the `competition/` directory:
1.  **Submission Script (`submission.py` or similar)**: The primary entry point executed by Kaggle's evaluation environment.
2.  **Audit Reports**: Automated security audits of the PHP code.
3.  **Security Patches**: Safe modifications applying input escaping and prepared queries, preserving backward compatibility.
4.  **REST API endpoints**: Modern controllers in PHP to bridge Python-based AI agents.
5.  **Agent Logs**: Diagnostic execution summaries detailing prompt token costs and verification success rates.
