# Calligraphy Central - Project Task Board

This document lists the tasks required to build out the Calligraphy Central agentic application.

---

## 📅 Phase 1: Scaffolding, Documentation & Skills
*   [x] Create Project Constitution (`PROJECT_CONSTITUTION.md`)
*   [x] Create Project Specification (`PROJECT_SPEC.md`)
*   [x] Create System Architecture (`ARCHITECTURE.md`)
*   [x] Create Capstone Requirements (`CAPSTONE_REQUIREMENTS.md`)
*   [x] Create Development Roadmap (`ROADMAP.md`)
*   [x] Create Project Task Board (`TODO.md`)
*   [x] Create specialized skill configuration files (`.agent/skills/*/SKILL.md`) [In Progress]
*   [x] Create supporting folders: `docs`, `agents`, `memory`, `competition`, `evaluation`, `python_ai`, `api`, `assets` [In Progress]
*   [x] Run validation script to confirm all folder layouts are present.

## 🔒 Phase 2: Security Auditing & Remediation
*   [x] Perform audit of PHP source files for vulnerability hot-spots.
*   [x] Replace direct database values in queries with parameterized inputs.
*   [x] Apply input sanitization and html escaping to views.
*   [x] Secure the upload processor to restrict executable payloads in the file storage tree.

## 🧪 Phase 3: Testing & Regression Prevention
*   [ ] Write a mock database initialization script for testing.
*   [ ] Write validation suites for basic login and registration routes.
*   [ ] Implement automated verification of image/video feed display.

## 🔌 Phase 4: API Connectivity Layer
*   [ ] Build PHP REST interfaces to feed artwork, likes, and comment threads.
*   [ ] Configure API tokens or session-based API protection models.

## 🧠 Phase 5: Python AI Agents
*   [ ] Build Python script to analyze artwork descriptions using Gemini models.
*   [ ] Build automated content moderator running validation loops on comments.
*   [ ] Output agent action traces to the `memory/` folder.

## 🏁 Phase 6: Capstone Validation
*   [ ] Bundle required Kaggle execution scripts inside `competition/`.
*   [ ] Verify the execution behavior of the submission entry script under a clean environment setup.
