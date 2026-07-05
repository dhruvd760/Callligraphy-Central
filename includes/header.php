<?php
include_once 'includes/session_config.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calligraphy Central</title>
    <link rel="stylesheet" href="style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Quintessential&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Moon+Dance&display=swap" rel="stylesheet">
</head>
<body>

<div class="container">
    <div class="bkgimg"></div>   
    <div class="head">Calligraphy Central</div>
    <input type="checkbox" id="check">
    <label for="check" class="sidebar-overlay"></label>
    <script>
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const cb = document.getElementById('check');
                if(cb && cb.checked) cb.checked = false;
            }
        });
    </script>
    
    
     <div class="hamburger">   
        <label for="check">
        <div class="bar"></div>
        <div class="bar"></div>
        <div class="bar"></div>
        </label>
    </div>    
    <div class="menu">
       <div class="over"></div>
        <nav class="list" >
            
            <ul class="ul1">
                <li class="mob"><a href="index.php">Home</a></li>
                <li class="mob"><a href="modern.php">Modern Calligraphy</a></li>
                <!-- <li class="mob"><a href="getting-started.php">Getting Started</a></li> -->
                <li class="mob"><a href="basics.php">Basics</a></li>
                <li class="mob"><a href="gallery.php">Gallery</a></li>
                
                <?php if(isset($_SESSION['user_id'])): ?>
                    <?php if($_SESSION['role'] === 'admin'): ?>
                        <li class="mob"><a href="admin_dashboard.php" style="color: #ff4444;">Admin Panel</a></li>
                    <?php endif; ?>

                    <li class="mob"><a href="upload.php">Upload Art</a></li>
                    <li><a href="my_posts.php">My Posts</a></li>
                    <li><a href="progress.php" style="color: #4a3b3b; font-weight: bold;">AI Progress</a></li>
                    <li class="mob"><a href="logout.php">Logout</a></li>
                <?php else: ?>
                    <li class="mob"><a href="login.php">Login</a></li>
                    <li class="mob"><a href="register.php">Sign Up</a></li>
                <?php endif; ?>
                
            </ul>
        </nav>
    </div>
   