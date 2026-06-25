# HTTP Security Headers Audit Report

This report documents the security audit performed on the HTTP response headers and session cookie parameters of the **Calligraphy Central** application. The audit verifies defenses against Cross-Site Scripting (XSS), Clickjacking, MIME-sniffing, cross-site leaks, session hijacking, and client-side device API access.

---

## 1. Audit Methodology & Scope

The audit evaluates all HTTP headers emitted by the Calligraphy Central application. We inspected:
*   The centralized security headers module: [includes/security_headers.php](file:///c:/xampp/htdocs/calligraphy_project/includes/security_headers.php)
*   The global session bootstrapper: [includes/session_config.php](file:///c:/xampp/htdocs/calligraphy_project/includes/session_config.php)
*   The HTTPS enforcement and HSTS module: [includes/https_enforcement.php](file:///c:/xampp/htdocs/calligraphy_project/includes/https_enforcement.php)
*   All user-facing controllers (e.g., `index.php`, `login.php`, `register.php`, `gallery.php`, `admin_dashboard.php`, `upload.php`) to confirm global bootstrapping coverage.

Only defensive auditing was performed to assess compliance and security hygiene.

---

## 2. Header Verification & Analysis

### 2.1 Content-Security-Policy (CSP)
*   **Emitted Header Value**:
    ```http
    Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com https://fonts.googleapis.com; img-src 'self' data:; media-src 'self'; object-src 'none'; frame-ancestors 'self'; base-uri 'self'; form-action 'self'
    ```
*   **Directives Analysis**:
    *   `default-src 'self'`: **Secure**. Restricts fetching of assets (scripts, styles, images) to the host origin by default.
    *   `script-src 'self' 'unsafe-inline'`: **Conservative / Functional Requirement**. Permits execution of local script files and inline scripts. While `'unsafe-inline'` is necessary to support legacy event handlers in `admin_dashboard.php` (such as `onmouseover`, `onmouseout`, `onclick` for hover video play), it limits defense-in-depth against XSS if input sanitization fails elsewhere.
    *   `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com`: **Conservative / Functional Requirement**. Allows local stylesheets, inline style attributes (used for UI margins and forms), and Google Fonts CDNs.
    *   `font-src 'self' https://fonts.gstatic.com https://fonts.googleapis.com`: **Secure**. Whitelists fonts from local origins and Google Font domains.
    *   `img-src 'self' data:`: **Secure**. Permits rendering local images and data URIs (e.g., base64 SVGs).
    *   `media-src 'self'`: **Secure**. Limits media source playback to local directories (e.g., video uploads).
    *   `object-src 'none'`: **Secure**. Prevents execution of plugins such as Flash, PDF viewers, or Java applets.
    *   `frame-ancestors 'self'`: **Secure**. Restricts other websites from framing this application, mitigating Clickjacking.
    *   `base-uri 'self'`: **Secure**. Restricts `<base>` tags to the local origin to prevent base-URI hijacking.
    *   `form-action 'self'`: **Secure**. Restricts form submission targets to the current domain, preventing credential harvesting redirects.
*   **Audit Status**: **PASSED (Hardened with Functional Compatibility)**

### 2.2 X-Frame-Options
*   **Emitted Header Value**:
    ```http
    X-Frame-Options: SAMEORIGIN
    ```
*   **Analysis**: Tells the browser that the page can only be displayed in a frame if the frame origin matches the page origin. This provides strong client-side clickjacking prevention for legacy browsers that do not support the CSP `frame-ancestors` directive.
*   **Audit Status**: **PASSED**

### 2.3 X-Content-Type-Options
*   **Emitted Header Value**:
    ```http
    X-Content-Type-Options: nosniff
    ```
*   **Analysis**: Prevents browsers from analyzing (MIME-sniffing) the content of resources to determine their content type, forcing them to adhere strictly to the `Content-Type` declared by the server. This neutralizes attacks where malicious scripts are disguised as benign assets (e.g., user-uploaded image files).
*   **Audit Status**: **PASSED**

### 2.4 Referrer-Policy
*   **Emitted Header Value**:
    ```http
    Referrer-Policy: strict-origin-when-cross-origin
    ```
*   **Analysis**: Instructs the browser to send full referrer path information for same-origin requests, but only send the domain origin for cross-origin requests, and nothing for HTTP-downgrade requests. This prevents sensitive URL parameters and query values from leaking to external domains.
*   **Audit Status**: **PASSED**

### 2.5 Permissions-Policy
*   **Emitted Header Value**:
    ```http
    Permissions-Policy: geolocation=(), camera=(), microphone=()
    ```
*   **Analysis**: Restricts browser access to hardware APIs. Specifying empty parenthesis lists `()` disables geolocation, camera access, and audio capture, reducing the surface area for client device exploit vectors.
*   **Audit Status**: **PASSED**

### 2.6 Strict-Transport-Security (HSTS)
*   **Emitted Header Value** (Only in Non-Local / Production over HTTPS):
    ```http
    Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
    ```
*   **Analysis**: Configured inside [includes/https_enforcement.php](file:///c:/xampp/htdocs/calligraphy_project/includes/https_enforcement.php). If the host is not localhost/loopback, the server forces the browser to connect exclusively via HTTPS for the next 1 year (31,536,000 seconds), including all subdomains, and requests inclusion in browser preloading lists. This protects against SSL stripping attacks.
*   **Audit Status**: **PASSED**

### 2.7 Session Cookie Security Headers
*   **Emitted Header Value** (`Set-Cookie` parameters):
    *   `HttpOnly`: **True** (Blocks JavaScript access to the session cookie, neutralizing session theft via XSS).
    *   `SameSite`: **Strict** (Instructs browsers to never send the cookie with cross-site requests, mitigating CSRF).
    *   `Secure`: **Conditional** (Only set to true when HTTPS is detected, ensuring session cookies are not sent over plaintext HTTP).
*   **Audit Status**: **PASSED**

---

## 3. Global Routing Coverage Audit

We verified the global bootloader pattern to ensure no entry point bypasses these headers:
1.  **Central Initialization**: [includes/session_config.php](file:///c:/xampp/htdocs/calligraphy_project/includes/session_config.php) loads `https_enforcement.php` and `security_headers.php` before starting any session or output.
2.  **Controller Inclusion**: All main page templates (`index.php`, `gallery.php`, `view_post.php`, `upload.php`, `my_posts.php`, `edit_posts.php`, `admin_dashboard.php`, `login.php`, `register.php`, `logout.php`, `basics.php`, `modern.php`, `getting-started.php`) include `includes/header.php` or `includes/session_config.php` directly at the top.
3.  **Action Handlers**: Independent action processors such as `delete_post.php`, `like_posts.php`, and `submit_comments.php` require and verify session parameters by including `includes/session_config.php` as their first step.
4.  **Coverage Conclusion**: **100% of executable entry points emit the required security headers before rendering headers or body markup.**

---

## 4. Identified Missing Protections & Future Recommendations

Although the primary security headers are active and correctly configured, the following enhancements are identified to further strengthen the application's defense-in-depth posture:

### 4.1 Cross-Origin Isolations (COOP / CORP / COEP)
*   **Missing Header**: `Cross-Origin-Opener-Policy: same-origin` (COOP)
    *   *Risk*: Without COOP, a cross-origin window opened by this site (or vice versa) can retain access to `window.opener`, exposing the site to cross-window interactions and Spectre-like side-channel attacks.
    *   *Remediation*: Configure `header("Cross-Origin-Opener-Policy: same-origin");` in [includes/security_headers.php](file:///c:/xampp/htdocs/calligraphy_project/includes/security_headers.php).
*   **Missing Header**: `Cross-Origin-Resource-Policy: same-origin` (CORP)
    *   *Risk*: Without CORP, external origins can fetch resources (images, styling, user scripts) from this application directly.
    *   *Remediation*: Configure `header("Cross-Origin-Resource-Policy: same-origin");` in [includes/security_headers.php](file:///c:/xampp/htdocs/calligraphy_project/includes/security_headers.php).
*   **Missing Header**: `Cross-Origin-Embedder-Policy: require-corp` (COEP)
    *   *Risk*: Allows embedding of arbitrary cross-origin resources.
    *   *Remediation*: If strict isolation is required, apply `header("Cross-Origin-Embedder-Policy: require-corp");`.

### 4.2 Legacy XSS Browser Protections
*   **Missing Header**: `X-XSS-Protection: 1; mode=block`
    *   *Risk*: Modern browsers ignore this in favor of CSP, but older legacy browsers might still benefit from standard XSS filtering block options.
    *   *Remediation*: Configure `header("X-XSS-Protection: 1; mode=block");` in [includes/security_headers.php](file:///c:/xampp/htdocs/calligraphy_project/includes/security_headers.php).

### 4.3 Content-Security-Policy Without `'unsafe-inline'`
*   **Directives Vulnerability**: The inclusion of `'unsafe-inline'` under `script-src` and `style-src` is a known security trade-off. If a malicious input bypasses sanitation and is rendered dynamically, it can execute scripts directly.
*   **Remediation**:
    1.  **Refactoring Inline JS**: Extract inline event listeners (like hover/click animations on `admin_dashboard.php`) into external, static Javascript bundles.
    2.  **CSP Nonces/Hashes**: Implement a dynamic, cryptographically secure nonce generated per-request inside [includes/session_config.php](file:///c:/xampp/htdocs/calligraphy_project/includes/session_config.php) (e.g. `$_SESSION['csp_nonce'] = bin2hex(random_bytes(16));`).
    3.  Pass the nonce to script tags: `<script nonce="<?= $_SESSION['csp_nonce'] ?>">`.
    4.  Update CSP to whitelist scripts matching the nonce: `script-src 'self' 'nonce-...'`.
