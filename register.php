<?php 
include 'includes/db_connect.php'; 
include 'includes/csrf.php';
include 'includes/header.php'; 

$msg = "";
if(isset($_POST['reg_btn'])) {
    verifyCSRFToken();

    include_once 'includes/register_rate_limit.php';
    $rate_limit_check = checkRegisterRateLimit($conn);

    if ($rate_limit_check['locked']) {
        $minutes = ceil($rate_limit_check['remaining'] / 60);
        $msg = "Too many registration attempts. Please try again in $minutes minute(s).";
    } else {
        recordRegistrationAttempt($conn);
        $username = $_POST['username'];
        $email = $_POST['email'];
        
        $raw_password = $_POST['password'];

        // Validate password constraints
        if (strlen($raw_password) < 8) {
            $msg = "Password must be at least 8 characters long.";
        } elseif (!preg_match('/[A-Z]/', $raw_password)) {
            $msg = "Password must contain at least one uppercase letter.";
        } elseif (!preg_match('/[0-9]/', $raw_password)) {
            $msg = "Password must contain at least one digit.";
        } else {
            // 1. Password hashing for additional security
            $password = password_hash($raw_password, PASSWORD_DEFAULT);

            // 2. SECURE Duplicate Check (Prepared Statement)
            $stmt = $conn->prepare("SELECT email FROM users WHERE email = ?");
            $stmt->bind_param("s", $email);
            $stmt->execute();
            $check = $stmt->get_result();
            
            if($check->num_rows > 0){
                $msg = "Email already exists!";
            } else {
                // 3. SECURE Insertion (Prepared Statement)
                $insert = $conn->prepare("INSERT INTO users (username, email, password) VALUES (?, ?, ?)");
                $insert->bind_param("sss", $username, $email, $password);
                
                if ($insert->execute()) {
                    $msg = "<span style='color:green'>Success! <a href='login.php'>Login now</a></span>";
                } else {
                    error_log("Database error in register.php: " . $conn->error);
                    $msg = "An error occurred during registration. Please try again later.";
                }
            }
        }
    }
}
?>
 <div class="content">
<div style="text-align:center; max-width:70%; margin:20px auto; padding:30px; border:1px solid #4a3b3b; border-radius:25px; background-color:rgba(255, 255, 255, 0.43);">
    <h1>Sign Up</h1>
    <?php if($msg) echo "<p>$msg</p>"; ?>
    <form method="POST">
        <input type="hidden" name="csrf_token" value="<?= generateCSRFToken() ?>">
        <input type="text" name="username" placeholder="Username" required style="width:90%; border-radius:25px; padding:10px; margin:10px 0;"><br>
        <input type="email" name="email" placeholder="Email" required style="width:90%; border-radius:25px; padding:10px; margin:10px 0;"><br>
        <input type="password" name="password" placeholder="Password" required style="width:90%; border-radius:25px; padding:10px; margin:10px 0;"><br>
        <button type="submit" name="reg_btn" style="width:98%; padding:10px; background:#2f0404; border-radius:25px; color:white; border:none; cursor:pointer;">Sign Up</button>
    </form>
</div>

<?php include 'includes/footer.php'; ?>