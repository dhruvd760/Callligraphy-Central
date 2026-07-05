# Calligraphy Central

**Calligraphy Central** is an AI-powered social media platform for the digital calligraphy community, developed as part of the **Google × Kaggle Agentic AI Capstone**. At its core, the project demonstrates how an autonomous AI agent can modernize a legacy PHP web application by intelligently moderating user-generated content, improving software quality, and enhancing the overall user experience.

Rather than functioning as a traditional social media website, Calligraphy Central integrates an AI-powered moderation agent that autonomously evaluates uploaded artwork using **Google Gemini 2.5 Flash**. The agent performs content analysis, makes publication decisions, handles moderation failures safely, and assists in maintaining a secure and reliable platform while preserving the existing legacy architecture.

The repository showcases the application of agentic software engineering principles, combining autonomous reasoning, structured execution playbooks, memory-aware workflows, validation pipelines, and security-focused refactoring within a real-world web application.

---

# 🎯 Project Objective

The objective of Calligraphy Central is to demonstrate how autonomous AI agents can be integrated into an existing social media platform to modernize legacy software through intelligent content moderation, automated decision-making, improved security, enhanced maintainability, and robust software engineering practices. The project serves as a practical example of applying agentic AI to solve real-world challenges in digital content management while preserving and promoting calligraphic art.

---

# 🚀 Project Overview

Calligraphy Central is a multi-page PHP/MySQL web application designed for sharing and preserving calligraphic artwork.

## Features

- **User Authentication** – Register, Login, Logout, and Role-based Access (User/Admin).
- **Art Gallery** – Instagram-style gallery displaying uploaded images and videos.
- **Artwork Uploads** – Secure upload system supporting images and videos up to 50 MB.
- **Social Interaction** – Like and comment on individual artworks.
- **Admin Dashboard** – Moderate and remove inappropriate content.
- **AI Moderation** – Google Gemini autonomously evaluates uploaded artwork. AI-approved submissions are published immediately, while content that fails moderation is rejected. If the AI service is unavailable, uploads fail safely with a user-friendly message.
- **Responsive Design** – Optimized for desktop, tablet, and mobile devices.

---

# 🛠 Technology Stack

| Layer | Technology |
|--------|------------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | PHP (Procedural, MySQLi) |
| Database | MySQL / MariaDB |
| AI Integration | Google Gemini API (Gemini 2.5 Flash) |
| Development Environment | XAMPP / Apache + PHP + MySQL |

---

# 🔒 Security Features

The application implements several security improvements, including:

- Prepared SQL statements throughout the application
- CSRF protection for sensitive operations
- Secure file upload validation
- Role-based authentication and authorization
- Centralized configuration management
- AI-powered autonomous content moderation
- Rate limiting for authentication and user actions

---

# 📂 Repository Directory Guide

```text
├── .agent/
│   └── skills/          # Specialized markdown instructions for autonomous agents
├── agents/              # Autonomous AI agent configurations
├── api/                 # API endpoint handlers
├── assets/              # Images, icons, branding assets
├── competition/         # Kaggle submission resources
├── docs/                # Developer documentation
├── evaluation/          # Automated validation scripts
├── includes/            # Reusable PHP components
├── memory/              # Agent memory and execution logs
├── python_ai/           # Python AI orchestration modules
├── uploads/             # User uploaded media
├── database.sql         # Database schema
├── index.php            # Landing page
├── gallery.php          # Gallery page
├── upload.php           # Upload page
└── other PHP files      # Authentication, comments, likes, dashboard, etc.
```

---

# ⚙ Local Development Setup

## 1. Install XAMPP
Install XAMPP (or any Apache + PHP + MySQL environment).

## 2. Copy the Project
Copy the project into your web root.

Example:

```text
C:\xampp\htdocs\calligraphy_project\
```

## 3. Start Services

Start Apache and MySQL from the XAMPP Control Panel.

## 4. Create the Database

Open:

```text
http://localhost/phpmyadmin
```

Create a database named `calligraphy_db` and import `database.sql`.

## 5. Configure Database Connection

Verify the credentials in `includes/config.php`.

Default configuration:

- Host: localhost
- Username: root
- Password: (empty)
- Database: calligraphy_db

## 6. Configure AI Environment

Copy:

`python_ai/.env.example`

to:

`python_ai/.env`

Then add:

```env
GEMINI_API_KEY=your_api_key_here
```

## 7. Launch the Application

Open:

```text
http://localhost/calligraphy_project/
```

---

# 🤖 Google × Kaggle Agentic AI Capstone

This repository serves as the primary environment for autonomous software engineering agents to analyze, secure, refactor, and improve a legacy PHP application.

## System Architecture

### Architecture Components

**LLM Engine**

Uses Google's **Gemini 2.5 Flash** model via the Google AI Studio API for rapid reasoning, multi-file code auditing, and autonomous artwork moderation.

**Execution Playbooks**

Agent runtime actions are constrained by contextual playbooks located in `.agent/skills/`.

**Memory Management**

Execution logs, historical agent modifications, and multi-turn state contexts are maintained inside the `memory/` directory.

**Validation Subsystem**

Automated validation scripts inside `evaluation/` verify application routes and help ensure that agent-applied modifications do not introduce regressions or backend failures.

---

# 📋 Capstone Information

This project was developed as part of the **Google × Kaggle Agentic AI Capstone**.

Autonomous agents were used to:

- Audit legacy PHP code
- Improve application security
- Refactor database access
- Centralize configuration
- Implement AI-powered autonomous moderation
- Improve reliability through structured error handling and audit logging
- Enhance maintainability
- Document the software architecture in accordance with the project's engineering guidelines and Project Constitution

---

# 📄 License

This project is intended for educational purposes as part of the Google × Kaggle Agentic AI Capstone.
