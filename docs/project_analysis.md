# Technical Analysis Report: Calligraphy Central Base Codebase

This document presents a comprehensive technical audit of the legacy Calligraphy Central PHP/MySQL application. It analyzes the architectural patterns, dependencies, database schema constraints, code redundancies, technical debt, and critical security concerns before the introduction of testing infrastructure, APIs, or AI additions.

---

## 1. Architectural Patterns & Flow

Calligraphy Central is structured using a classic **Page Controller Pattern** combined with basic PHP dynamic template inclusions:

*   **Tightly Coupled Logic**: Individual `.php` scripts handle HTTP requests, perform input processing, manage database transactions, and generate the final HTML output.
*   **Template Modularization**: Reusable layout blocks are included at the top (`includes/header.php`) and bottom (`includes/footer.php`) of viewable pages.
*   **Dynamic Navigational Layout**: The navigation bar adjusts menu links (e.g., showing Upload, Portfolio, Admin Panel) based on the user's active `$_SESSION` properties.
*   **State Control**: Native PHP server-side sessions (`session_start()`) are used to persist authentication states across page transitions.

### Redirection Risk: "Headers Already Sent"
A recurring architectural flaw exists in scripts that execute authentication or action redirects (such as `login.php` or `register.php`).
*   **Problem**: In `login.php`, `includes/header.php` is included at line 7, generating immediate HTML output (HTTP headers, doctypes, body containers). If a user successfully authenticates on line 33, PHP attempts to trigger `header("Location: index.php")` on line 41.
*   **Implication**: Sending HTTP headers *after* outputting content will fail with a `"Headers already sent"` warning, preventing the redirect from firing unless output buffering (`output_buffering`) is explicitly enabled in `php.ini`. If buffering is turned off, the login flow breaks.

---

## 2. Dependency Registry

The application utilizes minimal, native server technologies:

1.  **Backend Runtime**: PHP 8.x (procedural script execution, mysqli extension).
2.  **Database Server**: MySQL 5.7+ / MariaDB 10.x.
3.  **UI Layout**: Vanilla CSS3 (`style.css`), relying on local layout rules.
4.  **Static Visual Media**: Local mockups and assets:
    *   `backg.png`, `calli_head001.png`, `lap_menu.png`, `mob.png`, `mob_menu.png`
5.  **External Web Fonts**:
    *   Google Fonts: *Quintessential* and *Moon Dance* loaded via remote preconnect tags in `includes/header.php`.

---

## 3. Database Schema Analysis

The relational schema is configured under the database `calligraphy_db` with four core tables:

### 3.1 Table Schemas

#### 1. `users`
Persists user profile information, auth credentials, and platform authorization roles:
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. `posts`
Stores artwork metadata, caption text descriptions, and points to saved media files:
```sql
CREATE TABLE posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(400),
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

#### 3. `likes`
A relationship pivot table tracking likes on posts. Features a composite unique key to enforce single likes:
```sql
CREATE TABLE likes (
    like_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    post_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);
```

#### 4. `comments`
Persists text comments linked to specific post pages and users:
```sql
CREATE TABLE comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

### 3.2 Relational Integrity
*   **Cascading Deletions**: Every foreign key is configured with `ON DELETE CASCADE`. If a post is deleted, its related likes and comments are cleaned up automatically. Similarly, deleting a user account cascades to wipe all their posts, comments, and likes, preventing orphaned records.

---

## 4. Code Duplication & Redundancy

Several features are implemented redundantly across multiple page controllers:

### 4.1 Media Render Branching
The code to check if a file is an image or video and output the correct HTML tag is duplicated across four files:
*   `gallery.php` (lines 31-41)
*   `admin_dashboard.php` (lines 24-25)
*   `my_posts.php` (lines 38-46)
*   `view_post.php` (lines 40-45)
Each page duplicates the string search block checking for the presence of `'image/'` or `'video/'` inside the database-stored `file_type` field.

### 4.2 Authorization Checks
Redundant verification blocks are used to enforce access restrictions:
*   Admin role checking is coded in `admin_dashboard.php` (line 5) and `delete_post.php` (line 13).
*   User session presence checks are implemented independently in `upload.php`, `my_posts.php`, `edit_posts.php`, `delete_post.php`, `like_posts.php`, and `submit_comments.php`.

### 4.3 Database Connection Setup
The line `include 'includes/db_connect.php';` is imported repeatedly in almost every controller file. A centralized router or auto-loading setup is absent.

---

## 5. Technical Debt Audit

The codebase displays several critical technical debt issues that impact scalability, debugging, and code structure:

1.  **Lack of Centralization**: Configuration parameters (database host, credentials, upload path mappings) are hardcoded. Changing a database setting requires editing files in multiple places.
2.  **Inconsistent Error Handling**: Error catching is rudimentary. Unsuccessful queries or operations result in direct script termination via `die()` or dump database connection details (`$conn->error`) directly onto the client viewport. This leaks configuration details and provides a poor user experience.
3.  **Inefficient Queries**:
    *   In `gallery.php` and `view_post.php`, the aggregate like counts are fetched using nested SQL subqueries: `(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count`. As the number of posts grows, this layout forces the database engine to run subqueries for every single row returned, rather than utilizing a cleaner `LEFT JOIN` and `GROUP BY` setup.
4.  **Implicit Type Mapping**: In `my_posts.php` (line 25), the database parameter binding binds `user_id` (an integer) as a string: `bind_param("s", $current_user)`. While MySQL handles type casting automatically, it introduces minor processing overhead and violates strict type practices.

---

## 6. Critical Security Observations

The following vulnerabilities and security weaknesses were identified in the codebase:

### 6.1 Critical Vulnerability: Insecure File Upload in Edit Mode (RCE)
*   **Vulnerability Location**: `edit_posts.php` (lines 40-60)
*   **Analysis**: When a user updates their artwork, they can optionally upload a new file. Unlike the initial upload script (`upload.php`) which enforces whitelist checking for image and video extensions, the edit script (`edit_posts.php`) has **no extension checks**. 
*   **Exploitation Route**: A registered user can edit an existing post and upload a malicious PHP web shell script (e.g., `shell.php`). The script will be saved directly into the `uploads/` directory. By requesting the URL `http://localhost/calligraphy_project/uploads/[timestamp]_shell.php`, the attacker can execute arbitrary code on the server, resulting in a complete host compromise.

### 6.2 Cross-Site Scripting (XSS)
*   **Vulnerability Location**: `admin_dashboard.php` (line 24)
*   **Analysis**: In the admin panel, the filename and file type attributes are rendered directly into HTML video and image tags:
    `"<video src='uploads/" . $row['file_name'] . "' ..."`
    If a file is uploaded with double quotes or HTML markup in its name (possible if file upload checks are bypassed or if the filename is manipulated during upload), it can lead to HTML attribute injection or XSS inside the administrator's dashboard session.
*   **Input Sanitization**: While comments, titles, and descriptions are escaped using `htmlspecialchars()` upon output in `view_post.php` and `gallery.php`, they are stored raw in the database. Any future page displaying comments without escaping will expose the application to Stored XSS.

### 6.3 Missing Cross-Site Request Forgery (CSRF) Defenses
*   **Vulnerability Location**: All form elements and action-executing GET requests.
*   **Analysis**: The application lacks CSRF token validation. An attacker can construct malicious forms or links on external sites targeting:
    *   `like_posts.php` (liking/unliking posts on behalf of the victim user)
    *   `submit_comments.php` (posting spam comments automatically)
    *   `delete_post.php?id=[post_id]` (tricking an admin or the owner into deleting arbitrary gallery items)
    Since actions do not validate unique session-bound CSRF tokens, these endpoints are fully vulnerable to unauthorized cross-site actions.

### 6.4 Weak Authentication Safeguards
*   **Lack of Password Constraints**: `register.php` validates that email and username fields are populated, but permits users to register extremely weak passwords (e.g., single-character values).
*   **Admin Access Leakage**: In `admin_dashboard.php`, the authorization verify block on line 5 occurs *after* the header is included. A guest requesting this page receives HTTP 200 containing the layout header and navigations, exposing the site structure before "Access Denied" terminates execution.
