# HTTPS Enforcement & Redirection Report

This report documents the security controls implemented to enforce production-ready HTTPS connections across the entire application, while bypassing local development configurations (such as XAMPP or localhost).

---

## 1. Executive Summary

We have integrated a centralized HTTPS detection and enforcement engine. It automatically redirects insecure HTTP requests targeting production servers to the secure HTTPS protocol, while preserving standard HTTP connections on local developer environments (like `localhost` or `127.0.0.1`), ensuring zero disruption to local testing.

---

## 2. Hardening Measures Implemented

### 2.1 Centralized Detection & Redirection
Created a centralized logic script at [includes/https_enforcement.php](file:///c:/xampp/htdocs/calligraphy_project/includes/https_enforcement.php) that executes the following checks:
1.  **Local Environment Bypass**: Inspects the incoming host (`$_SERVER['HTTP_HOST']`) and the remote client IP (`$_SERVER['REMOTE_ADDR']`). If either matches `localhost`, loopback addresses (`127.0.0.1` or `[::1]`), the redirection is bypassed to avoid interrupting developer XAMPP setups.
2.  **HTTPS Detection**: Verifies if HTTPS is active via `$_SERVER['HTTPS']` or standard HTTP proxy headers (`$_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https'`).
3.  **SEO-Compliant Redirection**: If the request is insecure and outside local scope, the client is redirected to the corresponding secure URL using a permanent redirection status header: `header("Location: https://...", true, 301)`.

### 2.2 Strict-Transport-Security (HSTS)
When a secure HTTPS request is validated in a production environment, the engine sends the following header:
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```
*   **Purpose**: Instructs modern browsers to automatically rewrite all future HTTP requests to this domain (and its subdomains) to HTTPS client-side for the next 1 year (31,536,000 seconds), protecting against SSL-stripping and protocol downgrade attacks.

---

## 3. Audited and Modified Files

| File Name | Security Change Description |
| :--- | :--- |
| **[includes/https_enforcement.php](file:///c:/xampp/htdocs/calligraphy_project/includes/https_enforcement.php)** | [NEW] Primary HTTPS detection and redirection helper implementing local network skips and HSTS delivery. |
| **[includes/session_config.php](file:///c:/xampp/htdocs/calligraphy_project/includes/session_config.php)** | [MODIFY] Loaded the enforcement script as the very first instruction before configuring session parameter variables, preventing "headers already sent" warnings on redirects. |

---

## 4. Verification and Functional Compatibility

*   **Syntax Integrity**: Confirmed all files compile without syntax errors via `php -l`.
*   **Local Compatibility**: Accessing the application via local loopback addresses or `localhost` loads pages over standard HTTP as expected without triggering redirection loops.
