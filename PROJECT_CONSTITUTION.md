# Calligraphy Central - Project Constitution

> [!IMPORTANT]
> **CONSTITUTIONAL HIERARCHY**: This document is the **highest authority** of the Calligraphy Central project. All subsequent plans, features, code modifications, or refactoring attempts must comply fully with the guidelines and mandates detailed herein.

---

## 1. Core Mandate

The primary goal of the Calligraphy Central project is to prepare the legacy PHP/MySQL application for the Google × Kaggle Agentic AI Capstone by introducing a robust documentation layer, agent skills layer, and standard folder boundaries **without disrupting or modifying the existing PHP user interface, database logic, or page controller architecture.**

---

## 2. Immutable Architecture Invariants

Any modification to Calligraphy Central must respect the following architectural invariants:

### 2.1 Technology Stack Preservation
*   **HTML**: Must remain the structure layer for the frontend pages.
*   **CSS**: Must remain the layout and style layer. No unapproved Tailwind CSS conversions or framework migrations. Style definitions reside strictly in `style.css`.
*   **PHP**: The application must continue to execute as a classic PHP multi-page website using the page controller pattern.
*   **MySQL**: The relational database layer is the single source of truth for persistence. No NoSQL or external database systems should be introduced.

### 2.2 Backward Compatibility
*   **Functional Parity**: All existing features (User Registration, Login, Feed/Gallery, Media Uploads, Comments, Likes, and Admin Dashboard) must continue to function exactly as currently written.
*   **No Preemptive Refactoring**: Refactoring code for the sake of "modernization" (e.g., rewriting procedural PHP into complex OOP/MVC frameworks) is strictly prohibited unless explicitly requested by the User.
*   **Visual Continuity**: The design assets, image dependencies (`backg.png`, `calli_head001.png`, `lap_menu.png`, `mob.png`, `mob_menu.png`), and styling flow must remain unchanged.

---

## 3. Agent & AI Boundaries

To fulfill the requirements of the Google × Kaggle Agentic AI Capstone, the project layout includes specialized directories for AI agents, memory, and orchestration:

### 3.1 AI Feature Isolation
*   **No PHP Page Modifications**: AI features, model integrations, or autonomous loops must not be injected into existing client-facing PHP pages at this stage.
*   **API Isolation**: Any future AI features must interact with the application through designated, secure endpoints under `/api/` or run asynchronously via Python scripting under `/python_ai/`.
*   **Security Sandboxing**: Agents operating in this environment are bound by strict security review rules. No executing arbitrary system commands or dropping validation checks.

### 3.2 Developer Skill Compliance
*   All developers (human or agentic) must read, load, and follow the instructions within the `.agent/skills/` directory when performing tasks in their respective domains.

---

## 4. Conflict Resolution

If a conflict arises between a newly proposed feature, an implementation plan, a Kaggle competition guideline, and this Constitution:
1.  **The Constitution wins by default.**
2.  Any deviation requires explicit written approval from the User.
3.  Amendments to this Constitution must be updated in this file.
