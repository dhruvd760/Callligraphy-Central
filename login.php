<?php 
// start session & connect DB before any HTML output
include_once 'includes/session_config.php';
include 'includes/db_connect.php'; 
include 'includes/csrf.php';
include 'includes/header.php'; 
// 2. Redirect if already logged in
if(isset($_SESSION['user_id'])) {
    header("Location: index.php");
    exit();
}

$msg = "";

if(isset($_POST['login_btn'])) {
    verifyCSRFToken();
    $email = $_POST['email'];
    $password = $_POST['password'];

    include_once 'includes/RateLimiter.php';
    $rate_limit_check = RateLimiter::checkLoginRateLimit($conn, $email);

    if ($rate_limit_check['locked']) {
        $minutes = ceil($rate_limit_check['remaining'] / 60);
        $msg = "Too many failed login attempts. Please try again in $minutes minute(s).";
    } else {
        // original idea that supports older versions of php
        $stmt = $conn->prepare("SELECT user_id, password, role FROM users WHERE email = ?");
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $result = $stmt->get_result();

        //new way to shorten above 4 lines in php 8.2+ versions
        // $result = $conn->execute_query("SELECT user_id, password, role FROM users WHERE email = ?", [$email]);
        
        //if a user is found with given credentials, log him in...
        if ($result->num_rows == 1) {
            $row = $result->fetch_assoc();
             $msg = "Email  found";
            if (password_verify($password, $row['password'])) {
                // Clear attempts on success
                RateLimiter::clearLoginAttempts($conn, $email);
                
                //session login/logout glitching fix (Prevents "Glitching/Logout")
                session_regenerate_id(true);       // Security: Get a fresh Session ID
                $_SESSION['user_id'] = $row['user_id'];
                $_SESSION['role'] = $row['role'];
                session_write_close();             // Critical: Force save before redirect

                header("Location: index.php");
                exit();
            } else {
                RateLimiter::recordFailedLoginAttempt($conn, $email);
                $msg = "Incorrect Password";
            }
        } else {
            RateLimiter::recordFailedLoginAttempt($conn, $email);
            $msg = "Email not found";
        }
        //part of original logic
        // $stmt->close();
    }
}
//include header here for original logic
?>
 <div class="content">
<div style="text-align:center; max-width:70%; margin:20px auto; padding:30px; border:1px solid #4a3b3b; border-radius:30px; background-color:rgba(255, 255, 255, 0.43);">
    <h1>Login</h1>
    <?php 
       if($msg) 
        echo "<p style='color:red'>$msg</p>"; 
    ?>
    <form method="POST">
        <input type="hidden" name="csrf_token" value="<?= generateCSRFToken() ?>">
        <input type="email" name="email" placeholder="Email" required style="width:90%; padding:10px; border-radius:25px; margin:10px 0;"><br>
        <input type="password" name="password" placeholder="Password" required style="width:90%; padding:10px; border-radius:25px; margin:10px 0;"><br>
        <button type="submit" name="login_btn" style="width:96%; padding:10px; border-radius:25px; background:#2f0404; color:white; border:none; cursor:pointer;">Login</button>
    </form>
</div>

<?php include 'includes/footer.php'; ?>