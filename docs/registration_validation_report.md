# Registration Password Complexity Audit Report

This report documents the security validation improvements introduced inside the registration logic of Calligraphy Central.

---

## 1. Summary of Registration Validation Audit

A review of the signup controller (`register.php`) revealed that password inputs were hashed securely using standard `password_hash()`, but lacked backend validation filters for password complexity. Users could register accounts using short or weak credentials (e.g. single-character passwords), leaving the platform vulnerable to automated brute-force attacks and compromising user base integrity.

---

## 2. Password Constraints Enforced

To align with modern web security best practices, we implemented strict registration checks on password parameters before execution of database duplicate queries or hashing routines:

1.  **Length Requirement**: Passwords must contain a **minimum of 8 characters** (`strlen() < 8`).
2.  **Uppercase Character Requirement**: Passwords must contain **at least one uppercase letter** (`A-Z` checked via `preg_match`).
3.  **Digit Requirement**: Passwords must contain **at least one numeric digit** (`0-9` checked via `preg_match`).

---

## 3. Remediated Code Details

### File: `register.php`
*   **Vulnerability Remediation**: Direct ingestion of password strings without structure verification.
*   **Fix Details**:
    *   Captured the raw password string input: `$raw_password = $_POST['password'];`
    *   Constructed a cascading validation tree:
        ```php
        if (strlen($raw_password) < 8) {
            $msg = "Password must be at least 8 characters long.";
        } elseif (!preg_match('/[A-Z]/', $raw_password)) {
            $msg = "Password must contain at least one uppercase letter.";
        } elseif (!preg_match('/[0-9]/', $raw_password)) {
            $msg = "Password must contain at least one digit.";
        } else {
            // Hashing and insertion
        }
        ```
    *   Maintained security-hardening parameters: The raw password is only handled within validation memory space, and the persistent column is written securely using `password_hash($raw_password, PASSWORD_DEFAULT)`.

---

## 4. Verification Status
*   **Safety Guards Active**: Weak inputs are rejected on the server side with informative instructions returned to the user response variable.
*   **Syntax Correctness**: Confirmed by local syntax checks. No parse warnings detected.
