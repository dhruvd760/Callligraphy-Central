# Calligraphy Central - Project Specification

This document details the functional capabilities, business rules, and specifications of Calligraphy Central.

---

## 1. User Roles and Access Control

The application supports three distinct user states:

| Feature / Action | Guest (Unauthenticated) | Registered User | Administrator |
| :--- | :---: | :---: | :---: |
| Browse Educational Content | Yes | Yes | Yes |
| View Gallery Feed | Yes | Yes | Yes |
| View Individual Posts & Comments | Yes | Yes | Yes |
| Like Posts | No | Yes | Yes |
| Write Comments | No | Yes | Yes |
| Upload Artwork / Media | No | Yes | Yes |
| Delete Own / Any Posts | No | No | Yes (Moderator) |
| Access Admin Dashboard | No | No | Yes |

---

## 2. Core Functional Requirements

### 2.1 Authentication & User Management
*   **Registration (`register.php`)**: Users must provide a username, email, and password. The system checks if the email is already registered, hashes the password using PHP's `password_hash()`, and saves the record with the default role `user`.
*   **Login (`login.php`)**: Validates email and password, initializes a secure PHP session, and stores `user_id`, `username`, and `role`.
*   **Logout (`logout.php`)**: Destroys the session and redirects the user to the landing page.

### 2.2 Educational & Resource Hub
*   **Homepage (`index.php`)**: Covers the definition of calligraphy, history across cultures (Indian, Arabic, Chinese, Western, Japanese), and the preservation movement.
*   **Other Resource Pages**:
    *   `basics.php`: Calligraphy tools, materials, and stroke practices.
    *   `modern.php`: Modern applications, calligraphy graffiti, typography, and lettering design.
    *   `getting-started.php`: Beginner guides and basic scripts.

### 2.3 Gallery & Feed (`gallery.php`)
*   Displays a responsive grid (`insta-grid`) of uploaded artwork posts ordered by the most recent upload date.
*   Determines if the uploaded file is an image or a video, rendering it using an `<img>` or `<video>` tag accordingly.
*   Shows metadata: username, upload date, post title, description caption, and likes count.
*   Provides buttons to view comments (`view_post.php`), like posts (`like_posts.php`), and share posts.
*   Admin-only delete buttons (`delete_post.php`) appear on each post card to allow content moderation.

### 2.4 Detail Post View & Comments (`view_post.php`)
*   Accessed via post links in the feed.
*   Displays the full-size media, post details (title, description, author, upload date), and a complete comment thread.
*   If authenticated, displays a comment submission form (`submit_comments.php`) to append text-based comments.

### 2.5 Media Upload (`upload.php`)
*   **Authorization**: Logged-out users are automatically redirected to `login.php`.
*   **Inputs**: Title (required), Description (optional, max 400 characters), and Media file (required).
*   **Validation**:
    *   Descriptions are validated both in the browser and backend to be $\le 400$ characters.
    *   Allowed file formats:
        *   Images: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp` (type mapped as `image/[ext]`).
        *   Videos: `.mp4`, `.avi`, `.mov`, `.mkv` (type mapped as `video/[ext]`).
    *   Size limits: Strictly capped at 50MB ($50 \times 1024 \times 1024$ bytes). Large payloads triggering empty `$_POST` variables are trapped and reported.
*   **Storage**: Files are saved to `uploads/` prefixed with a timestamp to prevent filename collision.

---

## 3. Database Schema Mapping

The system relies on a MySQL schema (`calligraphy_db`) comprising four tables:

1.  **`users`**: Stores credentials, roles, and creation timestamps.
2.  **`posts`**: Stores media metadata (filename, mime-type), title, description, and the uploading user's ID.
3.  **`likes`**: A pivot table linking users to posts they liked (composite unique index prevents duplicate likes by a single user).
4.  **`comments`**: Stores user text comments indexed by user and post.

*   *Note*: Foreign key constraints link `posts`, `likes`, and `comments` back to `users` and `posts` with `ON DELETE CASCADE` enabled. This guarantees integrity when a user account or post is deleted.
