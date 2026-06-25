# Calligraphy Central

Welcome to **Calligraphy Central**, a web platform dedicated to preserving, sharing, and reviewing calligraphic art. This repository is being prepared for the **Google × Kaggle Agentic AI Capstone**, serving as the target environment for autonomous agents to inspect, secure, and potentially extend a legacy web application.

---

## 🚀 Project Overview

Calligraphy Central is a classic multi-page PHP/MySQL web application. It features:
*   **User Accounts**: Register, Login, Logout, and roles (user, admin).
*   **Art Gallery / Feed**: An Instagram-like grid displaying uploaded images and videos of calligraphic work.
*   **Social Interactions**: Logged-in users can "like" posts and submit comments on individual post pages.
*   **Admin Tools**: Admin users can moderate content by deleting posts directly from the gallery feed.
*   **Media Uploads**: Secure file upload handling for images and video files under 50MB.

---

## 🛠️ Technology Stack

*   **Frontend**: Plain HTML5, CSS3 (`style.css`), Vanilla JavaScript.
*   **Backend**: PHP (Procedural, using database connections via MySQLi).
*   **Database**: MySQL/MariaDB (`database.sql`).
*   **Development Platform**: Designed to run seamlessly in local environments like XAMPP or standard Apache/PHP/MySQL stacks.

---

## 📂 Repository Directory Guide

```text
├── .agent/
│   └── skills/          # Specialized markdown instructions for autonomous agents
├── agents/              # Autonomous AI agent configurations and execution routines
├── api/                 # Endpoint routers and handlers for future service access
├── assets/              # Static media, icons, and branding materials
├── competition/         # Capstone submission files and Kaggle configuration details
├── docs/                # Supplementary design notes, developer guides, and analysis reports
├── evaluation/          # Validation scripts, unit tests, and performance benchmarks
├── includes/            # Reusable PHP templates (header, footer, database connect)
├── memory/              # Sandbox storage for agent transaction histories and state logs
├── python_ai/           # Python-based AI agentic integrations and model interaction layers
├── uploads/             # Directory where user-uploaded media files are persisted
├── database.sql         # Base database schema dump
├── index.php            # Homepage / Calligraphy history and preservation details
├── gallery.php          # Gallery feed dashboard
├── upload.php           # Post/Artwork submission page
└── [other PHP scripts]  # Authentication, likes, comments, and dashboard utilities
```

---

## ⚙️ Local Development Setup

To run Calligraphy Central locally:

1.  **Install XAMPP** (or any Apache + MySQL environment).
2.  **Clone / Copy** this repository into your web root directory:
    *   For XAMPP: `C:\xampp\htdocs\calligraphy_project\`
3.  **Start Apache and MySQL** via the XAMPP Control Panel.
4.  **Create the Database**:
    *   Open `http://localhost/phpmyadmin`.
    *   Create a new database named `calligraphy_db`.
    *   Import `database.sql` to populate the tables.
5.  **Configure Database Connection**:
    *   Verify credentials in `includes/db_connect.php`.
    *   Default settings target `localhost`, username `root`, empty password `""`, and database `calligraphy_db`.
6.  **Access the Application**:
    *   Navigate to `http://localhost/calligraphy_project/` in your web browser.

---

## 🤖 Google × Kaggle Agentic AI Capstone

This repository is optimized for autonomous software engineering agents.
*   **Rules of Engagement**: All modifications must obey the guidelines outlined in the [PROJECT_CONSTITUTION.md](file:///c:/xampp/htdocs/calligraphy_project/PROJECT_CONSTITUTION.md).
*   **Agent Skills**: The folder `.agent/skills/` contains explicit execution instructions for agent sub-systems, providing target-specific context for task planning.
*   **Testing & Evaluation**: See the `/evaluation/` folder for running validation test cases.
