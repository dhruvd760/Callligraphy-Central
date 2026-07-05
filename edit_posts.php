<?php
include_once 'includes/session_config.php';
include 'includes/db_connect.php';
include 'includes/csrf.php';

// Verify authentication
if (!isset($_SESSION['user_id'])) {
    writeSecurityLog('unauthorized_access', "Unauthenticated request to edit a post", [
        'post_id' => $_GET['id'] ?? 'unknown'
    ]);
    header("Location: login.php");
    exit();
}

// Check if ID is provided
if (!isset($_GET['id'])) {
    header("Location: gallery.php");
    exit();
}

$post_id = $_GET['id'];
$user_id = $_SESSION['user_id'];
$role = isset($_SESSION['role']) ? $_SESSION['role'] : 'user';

// 2. Fetch the Post
$sql = "SELECT * FROM posts WHERE post_id = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("i", $post_id);
$stmt->execute();
$result = $stmt->get_result();
$post = $result->fetch_assoc();

// 3. Check Ownership (Can this user edit this post?)
if (!$post || ($post['user_id'] != $user_id && $role != 'admin')) {
    writeSecurityLog('unauthorized_access', "User attempted to edit a post they do not own", [
        'post_id' => $post_id,
        'owner_id' => $post['user_id'] ?? 'none'
    ]);
    include 'includes/header.php'; // Load header just to show the error nicely
    echo "<div class='content'><h3>You cannot edit someone else's post.</h3></div>";
    include 'includes/footer.php';
    exit();
}

// Initialize an empty error message variable
$error_message = ""; 

// 4. Handle the Save Button
if (isset($_POST['update_post'])) {
    verifyCSRFToken();
    $new_title = $_POST['title'];
    $new_desc = $_POST['description'];
    
    // Check if a new image was uploaded
    if (!empty($_FILES['post_image']['name'])) {
        $file_name = $_FILES['post_image']['name'];
        $file_tmp = $_FILES['post_image']['tmp_name'];
        
        // Define 50MB limit in bytes
        $max_size_bytes = 50 * 1024 * 1024; 

        // Validate size
        if ($_FILES["post_image"]["error"] === UPLOAD_ERR_INI_SIZE) {
            writeSecurityLog('upload_validation_failed', "File exceeds server internal upload limit in edit mode", [
                'error_code' => $_FILES["post_image"]["error"]
            ]);
            $error_message = "Error: File exceeds the server's internal configuration upload limit.";
        } elseif ($_FILES["post_image"]["size"] > $max_size_bytes) {
            writeSecurityLog('upload_validation_failed', "File exceeds 50MB limit in edit mode", [
                'file_name' => $_FILES["post_image"]["name"] ?? 'unknown',
                'file_size' => $_FILES["post_image"]["size"] ?? 0
            ]);
            $error_message = "Error: The file is over the server limit. Please keep media under 50MB.";
        } else {
            // Generate a unique name
            $unique_file_name = time() . '_' . basename($file_name);
            $upload_dir = 'uploads/'; 
            $target_file = $upload_dir . $unique_file_name;
            $ext      = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));
            
            $allowed_images = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
            $allowed_videos = ['mp4', 'avi', 'mov', 'mkv'];

            // Logic to define $type correctly to match Gallery Dashboard logic
            if (in_array($ext, $allowed_videos)) {
                $type = 'video/' . $ext; // e.g., 'video/mp4'
            } elseif (in_array($ext, $allowed_images)) {
                $type = 'image/' . $ext; // e.g., 'image/png'
            } else {
                $type = 'unknown';
                writeSecurityLog('upload_validation_failed', "Invalid file format uploaded in edit mode", [
                    'file_name' => $_FILES["post_image"]["name"] ?? 'unknown',
                    'file_ext' => $ext
                ]);
                $error_message = "Invalid file format. Only JPG, PNG, MP4 allowed.";
            }

            if ($type != 'unknown' && empty($error_message)) {
                if (move_uploaded_file($file_tmp, $target_file)) {
                    // Delete old image
                    if (file_exists($upload_dir . $post['file_name'])) {
                        unlink($upload_dir . $post['file_name']);
                    }

                    // Update database WITH the new image
                    $update_sql = "UPDATE posts SET title=?, description=?, file_name=?, file_type=? WHERE post_id=?";
                    $up_stmt = $conn->prepare($update_sql);
                    $up_stmt->bind_param("ssssi", $new_title, $new_desc, $unique_file_name, $type, $post_id);
                } else {
                    writeSecurityLog('suspicious_activity', "Failed to move uploaded file in edit mode", [
                        'file_name' => $_FILES["post_image"]["name"] ?? 'unknown',
                        'target_path' => $target_file
                    ]);
                    $error_message = "Error uploading the new image. Please try again.";
                }
            }
        }
    } else {
        // Update database WITHOUT changing the image
        $update_sql = "UPDATE posts SET title=?, description=? WHERE post_id=?";
        $up_stmt = $conn->prepare($update_sql);
        $up_stmt->bind_param("ssi", $new_title, $new_desc, $post_id);
    }
    
    // Execute the query if it was prepared successfully
    if (isset($up_stmt) && $up_stmt && $up_stmt->execute()) {
        // REPLACED JS REDIRECT: Native PHP Redirect
        header("Location: gallery.php");
        exit(); // Always exit immediately after a header redirect
    } else if (empty($error_message)) {
        // If it failed and we haven't already set an upload error message
        $error_message = "Error updating post in the database.";
    }
}

// NOW that all background logic and redirects are done, load the visual header
include 'includes/header.php';
?>

<div class="content">

    <form method="post" enctype="multipart/form-data" class="glass-container">
        <input type="hidden" name="csrf_token" value="<?= generateCSRFToken() ?>">
        <h1>Edit Your Post</h1>
        
        <?php if (!empty($error_message)): ?>
            <div style="background-color: rgba(255, 0, 0, 0.2); border: 1px solid red; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
                <?php echo htmlspecialchars($error_message); ?>
            </div>
        <?php endif; ?>
        
        <div class="group-form" style="text-align: center; margin-bottom: 20px;">
            <p style="color: #fff; margin-bottom: 10px; font-size: 0.9em;">Current Media:</p>
            
            <?php if (str_starts_with($post['file_type'], 'video/')): ?>
                <video src="uploads/<?php echo htmlspecialchars($post['file_name']); ?>" controls style="max-width: 100%; max-height: 200px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);"></video>
            <?php else: ?>
                <img src="uploads/<?php echo htmlspecialchars($post['file_name']); ?>" alt="Current Post Media" style="max-width: 100%; max-height: 200px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <?php endif; ?>
            
        </div>

        <div class="group-form">
            <label>Title</label>
            <input type="text" name="title" class="glass-input" value="<?php echo htmlspecialchars($post['title']); ?>" required>
        </div>
        
        <div class="group-form">
            <label>Description</label>
            <textarea name="description" class="glass-input" rows="4"><?php echo htmlspecialchars($post['description']); ?></textarea>
        </div>
        
        <div class="group-form">
            <label>Change Image (Optional)</label>
            <input type="file" name="post_image" class="glass-input" accept="image/*">
        </div>
        
        <button type="submit" name="update_post" class="btn-ink">Save Changes</button>
        <a href="gallery.php" class="btn-cancel" style="display: inline-block; text-align: center; margin-top: 10px;">Cancel</a>
    </form>
</div>

<?php include 'includes/footer.php'; ?>