<?php
include_once 'includes/session_config.php';

// 1. Anti-Caching Headers (Forces the browser to ask the server for a fresh page)
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");

// 2. Security Check: If they are logged out, immediately kick them to login
if (!isset($_SESSION['user_id'])) {
    writeSecurityLog('unauthorized_access', "Unauthenticated request to upload.php");
    header("Location: login.php");
    exit();
}

include 'includes/db_connect.php';
include 'includes/csrf.php';

$msg = "";
$title_val = "";
$desc_val = "";

// 3. THE INVISIBLE CRASH CATCHER (Strictly PHP)
// Catches massive payloads that force the server to drop the $_POST array.
if ($_SERVER['REQUEST_METHOD'] == 'POST' && empty($_POST) && $_SERVER['CONTENT_LENGTH'] > 0) {
    writeSecurityLog('upload_validation_failed', "Massive file upload payload rejected", [
        'content_length' => $_SERVER['CONTENT_LENGTH']
    ]);
    $msg = "Error: The file is over the server limit. Please keep media under 50MB.";
} 
// 4. STANDARD UPLOAD PROCESSING
elseif (isset($_POST['upload'])) {
    verifyCSRFToken();
    
    // CAPTURE INPUTS & RETAIN THEM FOR THE UI
    $user_id   = $_SESSION['user_id'];
    $title_val = $_POST['title'];
    $desc_val  = $_POST['description'];

    // Define 50MB limit in bytes
    $max_size_bytes = 50 * 1024 * 1024; 

    // PHP VALIDATION TIER
    if (strlen($desc_val) > 400) {
        $msg = "Error: Description exceeds 400 characters.";
    } elseif (!isset($_FILES['file']) || $_FILES["file"]["error"] === UPLOAD_ERR_INI_SIZE) {
        writeSecurityLog('upload_validation_failed', "File exceeds server internal upload limit", [
            'error_code' => $_FILES["file"]["error"] ?? 'no_file'
        ]);
        $msg = "Error: File exceeds the server's internal configuration upload limit.";
    } elseif ($_FILES["file"]["size"] > $max_size_bytes) {
        writeSecurityLog('upload_validation_failed', "File exceeds 50MB limit", [
            'file_name' => $_FILES["file"]["name"] ?? 'unknown',
            'file_size' => $_FILES["file"]["size"] ?? 0
        ]);
        $msg = "Error: The file is over the server limit. Please keep media under 50MB.";
    } else {
        // File Handling
        $fileName = time() . "_" . basename($_FILES["file"]["name"]);
        $target   = "uploads/" . $fileName;
        $ext      = strtolower(pathinfo($target, PATHINFO_EXTENSION));
        
        $allowed_images = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
        $allowed_videos = ['mp4', 'avi', 'mov', 'mkv'];

        // Logic to define $type correctly to match Gallery Dashboard logic
        if (in_array($ext, $allowed_videos)) {
            $type = 'video/' . $ext; // e.g., 'video/mp4'
        } elseif (in_array($ext, $allowed_images)) {
            $type = 'image/' . $ext; // e.g., 'image/png'
        } else {
            $type = 'unknown';
            writeSecurityLog('upload_validation_failed', "Invalid file format uploaded", [
                'file_name' => $_FILES["file"]["name"] ?? 'unknown',
                'file_ext' => $ext
            ]);
            $msg = "Invalid file format. Only JPG, PNG, MP4 allowed.";
        }

        // Final Secure Save
        if ($type != 'unknown' && empty($msg)) {
            if (move_uploaded_file($_FILES["file"]["tmp_name"], $target)) {
                
                // Prepared Statement to prevent SQL Injection
                $stmt = $conn->prepare("INSERT INTO posts (user_id, title, file_name, file_type, description) VALUES (?, ?, ?, ?, ?)");
                $stmt->bind_param("issss", $user_id, $title_val, $fileName, $type, $desc_val);
                
                if ($stmt->execute()) {
                    header("Location: gallery.php");
                    exit();
                } else {
                    error_log("Database error in upload.php: " . $conn->error);
                    $msg = "Database Error: An error occurred while saving the post.";
                }
            } else {
                writeSecurityLog('suspicious_activity', "Failed to move uploaded file. Check folder permissions.", [
                    'file_name' => $_FILES["file"]["name"] ?? 'unknown',
                    'target_path' => $target
                ]);
                $msg = "Failed to upload file. Check folder permissions.";
            }
        }
    }
}

include 'includes/header.php';
?>

<div class="content">
    <div class="upload-wrapper">
        <h1 class="upload-header-title">Post to Gallery-Feed</h1>
        <br>
        
        <?php if ($msg != ""): ?>
            <p class="upload-alert-msg" style="background-color: rgba(255, 0, 0, 0.2); border: 1px solid red; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 15px;">
                <?php echo htmlspecialchars($msg); ?>
            </p>
        <?php endif; ?>

        <form method="post" enctype="multipart/form-data" class="upload-form">
            <input type="hidden" name="csrf_token" value="<?= generateCSRFToken() ?>">
            <div class="upload-field-container">
                <label>Title</label>
                <input type="text" name="title" required value="<?php echo htmlspecialchars($title_val); ?>" class="upload-input">
            </div>

            <div class="upload-field-container">
                <label>Description</label>
                <textarea name="description" rows="3" columns="5" maxlength="400" placeholder="Type here..." class="upload-input"><?php echo htmlspecialchars($desc_val); ?></textarea>
                <small class="upload-hint">Browser limit: 400 characters.</small>
            </div>

            <div class="upload-field-container sm-text">
                <label>Select Media</label>
                <input type="file" name="file" accept="image/*,video/*" required class="upload-input-file">
                <small class="upload-hint" style="display: block; margin-top: 5px;">Max file size: 50MB</small>
            </div>

            <button type="submit" name="upload" class="upload-action-btn">Share Post</button>
        </form>
    </div>
</div>

<?php include 'includes/footer.php'; ?>