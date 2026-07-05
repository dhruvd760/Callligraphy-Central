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
require_once __DIR__ . '/includes/AIService.php';

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
    $max_size_bytes = APP_MAX_UPLOAD_SIZE_BYTES; 

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
        $allowed_videos = ['mp4', 'mov', 'avi', 'webm'];

        // Logic to define $type correctly to match Gallery Dashboard logic
        if (in_array($ext, $allowed_videos)) {
            if ($ext === 'mov') {
                $type = 'video/quicktime';
            } elseif ($ext === 'avi') {
                $type = 'video/x-msvideo';
            } elseif ($ext === 'webm') {
                $type = 'video/webm';
            } else {
                $type = 'video/mp4';
            }
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
                    $post_id = $conn->insert_id;
                    error_log("Upload success: Post $post_id created.");
                    
                    // Execute AI moderation decision and finalize publication workflow.
                    $aiService = new AIService($conn);
                    
                    try {
                        $evalData = $aiService->evaluatePost($title_val, $desc_val, realpath($target), $type, $fileName, $user_id, $post_id);
                    } catch (Exception $e) {
                        error_log("AI Evaluation Exception for post {$post_id}: " . $e->getMessage());
                        $evalData = null;
                    }

                    if (!$evalData) {
                        error_log("Upload succeeded, but AI evaluation failed for post {$post_id}. Cleaning up.");
                        $evalData = [
                            'approved' => false,
                            'ai_available' => false,
                            'relevance_score' => 0,
                            'moderation_reason' => 'AI Evaluation unavailable due to API timeout or error.'
                        ];
                    } else {
                        // Save unified evaluation data if it exists
                        if (!$aiService->updatePost($post_id, $evalData)) {
                            error_log("Failed to save AI analysis data for post {$post_id}.");
                        }
                        if (!$aiService->updateModeration($post_id, $evalData)) {
                            error_log("Failed to save moderation data for post {$post_id}.");
                        }
                    }

                    // Handle AI-First Publishing workflow
                    $isSafe = (isset($evalData['approved']) && $evalData['approved'] === true);
                    $aiAvailable = $evalData['ai_available'] ?? true;

                    if (!$isSafe) {
                        $fileDeleted = 'no';
                        if (file_exists($target)) {
                            unlink($target);
                            $fileDeleted = 'yes';
                        }
                        $del_stmt = $conn->prepare("DELETE FROM posts WHERE post_id = ?");
                        $del_stmt->bind_param("i", $post_id);
                        $dbDeleted = $del_stmt->execute() ? 'yes' : 'no';
                        $del_stmt->close();
                        
                        $conf = $evalData['relevance_score'] ?? 'N/A';
                        $reason = $evalData['moderation_reason'] ?? 'None';
                        
                        $log_msg = "[AI MODERATION]\n" .
                                   "Post: {$post_id}\n" .
                                   "User: {$user_id}\n" .
                                   "Original filename: " . ($_FILES['file']['name'] ?? 'unknown') . "\n" .
                                   "Stored filename: {$fileName}\n" .
                                   "AI confidence: {$conf}\n" .
                                   "Approval boolean: false\n" .
                                   "Reason: {$reason}\n" .
                                   "File Deleted: {$fileDeleted}\n" .
                                   "Database Deleted: {$dbDeleted}";
                        error_log($log_msg);
                        
                        if (!$aiAvailable) {
                            $msg = "AI moderation is temporarily unavailable. Your upload could not be processed at this time. Please try again in a few minutes.";
                        } else {
                            $msg = "Your upload could not be published because it did not satisfy the platform's AI moderation checks. Please upload an original calligraphy artwork that complies with the community guidelines.";
                        }
                    } else {
                        header("Location: my_posts.php?upload_status=approved");
                        exit();
                    }
                    // --- END AI EVALUATION ---
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

<!-- Loading Overlay Styles -->
<style>
    #ai-loading-overlay {
        display: none;
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.8);
        z-index: 9999;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        font-family: 'Inter', sans-serif;
    }
    .ai-spinner {
        border: 6px solid #f3f3f3;
        border-top: 6px solid #b71c1c;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>

<div id="ai-loading-overlay">
    <div class="ai-spinner"></div>
    <h2 style="margin:0; font-weight: 300;">Analyzing Calligraphy...</h2>
    <p style="color: #bbb; margin-top: 10px;">Our AI Master is reviewing your strokes.</p>
</div>

<div class="content">
    <div class="upload-wrapper">
        <h1 class="upload-header-title">Post to Gallery-Feed</h1>
        <br>
        
        <?php if ($msg != ""): ?>
            <p class="upload-alert-msg" style="background-color: rgba(255, 0, 0, 0.2); border: 1px solid red; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 15px;">
                <?php echo htmlspecialchars($msg); ?>
            </p>
        <?php endif; ?>

        <form method="post" enctype="multipart/form-data" class="upload-form" onsubmit="document.getElementById('ai-loading-overlay').style.display = 'flex';">
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