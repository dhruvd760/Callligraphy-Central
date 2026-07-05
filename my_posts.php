<?php
include_once 'includes/session_config.php';
include 'includes/db_connect.php';
include 'includes/csrf.php';

// If user is not logged in, they shouldn't see "My Posts"
if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit();
}

include 'includes/header.php';
?>

<div class="content">
    <h1 style="text-align: center; margin-bottom: 20px;">My Portfolio</h1>

    <?php if (isset($_GET['upload_status'])): ?>
        <?php if ($_GET['upload_status'] === 'approved'): ?>
            <div class="modern-alert success" id="status-alert">
                <span>✅ Your artwork has been published successfully.</span>
                <button class="close-btn" onclick="document.getElementById('status-alert').style.display='none'">&times;</button>
            </div>
        <?php endif; ?>
    <?php endif; ?>

    <?php
    // --- STATISTICS DASHBOARD ---
    $current_user = $_SESSION['user_id'];
    $stats_sql = "
        SELECT 
            COUNT(p.post_id) as total_posts,
            SUM(CASE WHEN p.ai_moderation_status = 'Approved' OR p.ai_moderation_status IS NULL THEN 1 ELSE 0 END) as approved_posts,
            SUM(CASE WHEN p.ai_moderation_status = 'Review' THEN 1 ELSE 0 END) as review_posts,
            SUM(CASE WHEN p.ai_moderation_status = 'Flagged' THEN 1 ELSE 0 END) as flagged_posts,
            (SELECT COUNT(*) FROM likes l JOIN posts p2 ON l.post_id = p2.post_id WHERE p2.user_id = ?) as total_likes
        FROM posts p 
        WHERE p.user_id = ?
    ";
    $stats_stmt = $conn->prepare($stats_sql);
    $stats_stmt->bind_param("ii", $current_user, $current_user);
    $stats_stmt->execute();
    $stats_row = $stats_stmt->get_result()->fetch_assoc();
    
    $total_posts = $stats_row['total_posts'] ?? 0;
    $approved_posts = $stats_row['approved_posts'] ?? 0;
    $total_likes = $stats_row['total_likes'] ?? 0;
    ?>
    <div class="portfolio-stats-grid">
        <div class="stat-card">
            <h3>Total Artworks</h3>
            <p><?= htmlspecialchars($total_posts) ?></p>
        </div>
        <div class="stat-card">
            <h3>Published</h3>
            <p><?= htmlspecialchars($approved_posts) ?></p>
        </div>
        <div class="stat-card">
            <h3>Total Likes</h3>
            <p><?= htmlspecialchars($total_likes) ?></p>
        </div>
    </div>
    <!-- --- END STATISTICS DASHBOARD --- -->

    <div class="insta-grid">
        <?php
        $current_user = $_SESSION['user_id'];
            $stmt = $conn->prepare("SELECT posts.*, users.username 
                FROM posts 
                JOIN users ON posts.user_id = users.user_id 
                WHERE posts.user_id = ? 
                ORDER BY posts.upload_date DESC");
    $stmt->bind_param("i", $current_user);
    $stmt->execute();
    $result = $stmt->get_result();

        // Fetch posts for the current user
        // $result = $conn->execute_query("SELECT * FROM posts WHERE user_id = ? ORDER BY upload_date DESC", [$current_user]);
        
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                $escaped_file_name = htmlspecialchars($row['file_name'], ENT_QUOTES, 'UTF-8');
                $escaped_file_type = htmlspecialchars($row['file_type'], ENT_QUOTES, 'UTF-8');
                $escaped_username = htmlspecialchars($row['username'], ENT_QUOTES, 'UTF-8');
                $escaped_title = htmlspecialchars($row['title'], ENT_QUOTES, 'UTF-8');
                $escaped_description = htmlspecialchars($row['description'], ENT_QUOTES, 'UTF-8');
                $escaped_post_id = htmlspecialchars($row['post_id'], ENT_QUOTES, 'UTF-8');

                echo '<div class="insta-card">';
                
                // --- MEDIA CONTENT DISPLAY ---
                echo '<div class="card-media">';
                // Robust check: if file_type contains 'image'
                if (strpos($row['file_type'], 'image') !== false) {
                    echo '<img src="uploads/' . $escaped_file_name . '" alt="Post" style="max-width: 100%; height: auto; display: block;">';
                } else {
                    echo '<video controls style="max-width: 100%; height: auto; display: block;">
                            <source src="uploads/' . $escaped_file_name . '" type="' . $escaped_file_type . '">
                            Your browser does not support the video tag.
                          </video>';
                }
                echo '</div>';
                // --- END MEDIA ---
 
                // --- CARD CONTENT ---
                
                // --- STATUS BADGES ---
                $mod_status = $row['ai_moderation_status'];
                $badge_class = 'approved';
                $badge_text = '🟢 Published';
                $badge_context = 'Visible in public gallery';

                if ($mod_status === 'Review') {
                    $badge_class = 'review';
                    $badge_text = '🟡 Under Review';
                    $badge_context = 'Waiting for administrator review';
                } elseif ($mod_status === 'Flagged') {
                    $badge_class = 'flagged';
                    $badge_text = '🔴 Rejected';
                    $badge_context = 'Image violates upload policy';
                }

                echo '<div class="card-content">';
                echo '<span class="username">@' . $escaped_username . '</span>';
                echo '<div class="card-header" style="align-items: center; margin-bottom: 5px;">';
               
                    echo '<span class="username">' . $escaped_title . ' <span class="status-badge ' . $badge_class . '">' . $badge_text . '</span></span>';
                    echo '<div class="action-buttons">';
                        echo '<a href="edit_posts.php?id=' . $escaped_post_id . '" class="edit-btn" style="margin-right: 10px;">EDIT</a>';
                        echo '<form action="delete_post.php" method="POST" style="display:inline; margin:0;" onsubmit="return confirm(\'Delete this post?\');">';
                        echo '<input type="hidden" name="id" value="' . $escaped_post_id . '">';
                        echo '<input type="hidden" name="csrf_token" value="' . generateCSRFToken() . '">';
                        echo '<button type="submit" class="delete-btn" style="background:none; cursor:pointer; font-family:inherit; outline:none; display:inline-block; line-height:normal;">DELETE</button>';
                        echo '</form>';
                    echo '</div>';
                echo '</div>';
                echo '<span class="status-context">' . $badge_context . '</span>';
                echo '<p class="caption">' . $escaped_description . '</p>';
                echo '</div>';
                // --- END CARD CONTENT ---

                echo '</div>';
            }
        } else {
            echo '<p style="text-align:center; width:100%;">You haven\'t uploaded anything yet.</p>';
            echo '<div style="text-align:center; width:100%; margin-top:20px;"><a href="upload.php" class="btn-login">Upload First Post</a></div>';
        }
        ?>
    </div>
</div>

<?php include 'includes/footer.php'; ?>