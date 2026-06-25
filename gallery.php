<?php
include_once 'includes/session_config.php';
include 'includes/db_connect.php';
include 'includes/csrf.php';
include 'includes/header.php';
?>

<div class="content">
    <h1>Calligraphy Feed</h1>
    
    <?php if (isset($_GET['msg']) && $_GET['msg'] == 'deleted'): ?>
        <p style="color: green; margin-bottom: 10px;">Post deleted successfully.</p>
    <?php endif; ?>

    <div class="insta-grid">
        <?php
        // Pagination logic
        $posts_per_page = 20;
        $page = isset($_GET['page']) && is_numeric($_GET['page']) ? (int)$_GET['page'] : 1;
        if ($page < 1) $page = 1;
        $offset = ($page - 1) * $posts_per_page;

        // Fetch posts and count likes simultaneously (retaining original query structure as mandated)
        $sql = "SELECT posts.*, users.username, 
                (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count 
                FROM posts 
                JOIN users ON posts.user_id = users.user_id 
                ORDER BY upload_date DESC LIMIT ? OFFSET ?";
        
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ii", $posts_per_page, $offset);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()): 
        ?>
            
            <div class="insta-card" id="post-<?= htmlspecialchars($row['post_id'], ENT_QUOTES, 'UTF-8'); ?>">
                
                <div class="card-media">
                    <?php 
                    // Robust check: if file_type contains 'image' (handles image/jpeg, image/png, etc.)
                    if (strpos($row['file_type'], 'image') !== false): 
                    ?>
                        <img src="uploads/<?= htmlspecialchars($row['file_name'], ENT_QUOTES, 'UTF-8'); ?>" alt="Artwork" style="max-width: 100%; height: auto; display: block;">
                    <?php else: ?>
                        <video controls style="max-width: 100%; height: auto; display: block;">
                            <source src="uploads/<?= htmlspecialchars($row['file_name'], ENT_QUOTES, 'UTF-8'); ?>" type="<?= htmlspecialchars($row['file_type'], ENT_QUOTES, 'UTF-8'); ?>">
                            Your browser does not support the video tag.
                        </video>
                    <?php endif; ?>
                </div>

                <div class="card-content">
                    
                    <div class="card-header">
                        <span class="username">@<?= htmlspecialchars($row['username'], ENT_QUOTES, 'UTF-8'); ?></span>
                        <?php if (isset($_SESSION['role']) && $_SESSION['role'] === 'admin'): ?>
                            <form action="delete_post.php" method="POST" style="display:inline; margin:0;" onsubmit="return confirm('Delete this post?');">
                                <input type="hidden" name="id" value="<?= htmlspecialchars($row['post_id'], ENT_QUOTES, 'UTF-8'); ?>">
                                <input type="hidden" name="csrf_token" value="<?= generateCSRFToken(); ?>">
                                <button type="submit" class="delete-btn" style="background:none; cursor:pointer; font-family:inherit; outline:none; display:inline-block; line-height:normal;">DELETE</button>
                            </form>
                        <?php endif; ?>
                    </div>

                    <div style="font-size: 16px; color: #888; margin-bottom: 8px;">
                        <?= date('F j, Y', strtotime($row['upload_date'])); ?>
                    </div>

                    <div class="interaction-bar" style="display: flex; gap: 15px; align-items: center; margin-bottom: 15px;">
                        
                        <?php if (isset($_SESSION['user_id'])): ?>
                            <form action="like_posts.php" method="POST" class="action-form" style="margin: 0;">
                                <input type="hidden" name="csrf_token" value="<?= generateCSRFToken(); ?>">
                                <input type="hidden" name="post_id" value="<?= htmlspecialchars($row['post_id'], ENT_QUOTES, 'UTF-8'); ?>">
                                <button type="submit" class="icon-btn" style="background: none; border: none; cursor: pointer; font-size: 1.1em;">
                                    ❤️ <?= htmlspecialchars($row['like_count'] ?? 0, ENT_QUOTES, 'UTF-8'); ?>
                                </button>
                            </form>
                        <?php else: ?>
                            <span class="icon-btn" style="cursor: default; font-size: 1.1em;">
                                ❤️ <?= htmlspecialchars($row['like_count'] ?? 0, ENT_QUOTES, 'UTF-8'); ?>
                            </span>
                        <?php endif; ?>

                        <a href="view_post.php?id=<?= htmlspecialchars($row['post_id'], ENT_QUOTES, 'UTF-8'); ?>" class="icon-btn" style="text-decoration: none; font-size: 1.1em;">
                            💬 Comment
                        </a>

                        <a href="view_post.php?id=<?= htmlspecialchars($row['post_id'], ENT_QUOTES, 'UTF-8'); ?>" class="icon-btn share-btn" style="text-decoration: none; font-size: 1.1em;">
                            🔗 Share
                        </a>
                    </div>

                    <?php if (!empty($row['title'])): ?>
                        <h3 class="post-title"><?= htmlspecialchars($row['title'], ENT_QUOTES, 'UTF-8'); ?></h3>
                    <?php endif; ?>
                    <div class="caption"><?= htmlspecialchars($row['description'], ENT_QUOTES, 'UTF-8'); ?></div>

                </div>
            </div>

        <?php 
            endwhile; 
        } else {
            echo '<p style="text-align:center; padding: 20px;">No posts available yet. Be the first to upload!</p>';
        }
        ?>
    </div>

    <!-- Pagination Controls -->
    <div style="text-align: center; margin: 20px 0;">
        <?php if ($page > 1): ?>
            <a href="?page=<?= $page - 1 ?>" style="padding: 10px 15px; background: #4a3b3b; color: white; text-decoration: none; border-radius: 5px; margin-right: 10px;">⬅ Previous</a>
        <?php endif; ?>
        
        <?php if ($result->num_rows == $posts_per_page): ?>
            <a href="?page=<?= $page + 1 ?>" style="padding: 10px 15px; background: #4a3b3b; color: white; text-decoration: none; border-radius: 5px;">Next ➡</a>
        <?php endif; ?>
    </div>
</div>

<?php include 'includes/footer.php'; ?>