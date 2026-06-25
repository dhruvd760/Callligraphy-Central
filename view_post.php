<?php
include_once 'includes/session_config.php';
include 'includes/db_connect.php';
include 'includes/csrf.php';
include 'includes/header.php';

// Check if an ID was passed in the URL
if (!isset($_GET['id']) || empty($_GET['id'])) {
    die("<div class='content'><h2>Post not found.</h2><a href='gallery.php'>Return to Gallery</a></div>");
}

$post_id = intval($_GET['id']);

// Fetch the specific post using a prepared statement
$sql = "SELECT posts.*, users.username, 
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count 
        FROM posts 
        JOIN users ON posts.user_id = users.user_id 
        WHERE posts.post_id = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("i", $post_id);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows == 0) {
    die("<div class='content'><h2>Post not found.</h2><a href='gallery.php'>Return to Gallery</a></div>");
}

$post = $result->fetch_assoc();
?>

<div class="content" style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 80vh; width: 100%;">

    <a href="gallery.php" style="display:block; margin-bottom: 20px; color: #4a3b3b; text-decoration: none;">
        ⬅ Back to Gallery
    </a>

    <div class="insta-card" style="width: 100%; max-width: 600px; background: white; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">

        
        

        <div class="card-media">
            <?php if (str_starts_with($post['file_type'],'image/')): ?>
                <img src="uploads/<?= htmlspecialchars($post['file_name'], ENT_QUOTES, 'UTF-8'); ?>" alt="Post"></img>
            <?php else: ?>
                <video controls><source src="uploads/<?= htmlspecialchars($post['file_name'], ENT_QUOTES, 'UTF-8'); ?>"></video>
            <?php endif; ?>
        </div>
        <br>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding: 0 5px;">
    
    <span class="username" style="font-size: 18px; font-weight: bold; color: #4a3b3b;">
        @<?= htmlspecialchars($post['username'], ENT_QUOTES, 'UTF-8'); ?>
    </span>

    <?php if (isset($_SESSION['user_id'])): ?>
        <form action="like_posts.php" method="POST" class="action-form" style="margin: 0;">
            <input type="hidden" name="csrf_token" value="<?= generateCSRFToken(); ?>">
            <input type="hidden" name="post_id" value="<?= htmlspecialchars($post['post_id'], ENT_QUOTES, 'UTF-8'); ?>">
            <button type="submit" class="icon-btn" style="margin: 0;">
                ❤️ <?= htmlspecialchars($post['like_count'] ?? 0, ENT_QUOTES, 'UTF-8'); ?>
            </button>
        </form>
    <?php else: ?>
        <div class="action-form" style="margin: 0;">
            <span class="icon-btn" style="cursor: default; pointer-events: none; margin: 0;">
                ❤️ <?= htmlspecialchars($post['like_count'] ?? 0, ENT_QUOTES, 'UTF-8'); ?>
            </span>
        </div>
        
    <?php endif; ?>
       
</div>
             
            <div style="margin: 15px 15px; padding: 10px; background: #f9f9f9; border: 1px solid #ddd; border-radius: 5px; align-self: center; width:90%;">
                <p style="margin: 0 0 5px 0; font-size: 13px; color: #555;  text-align:center;">Share this post:</p>
                <input type="text" value="http://<?= htmlspecialchars($_SERVER['HTTP_HOST'], ENT_QUOTES, 'UTF-8') . htmlspecialchars(dirname($_SERVER['PHP_SELF']), ENT_QUOTES, 'UTF-8'); ?>/view_post.php?id=<?= htmlspecialchars($post['post_id'], ENT_QUOTES, 'UTF-8'); ?>" readonly style="width: 90%; padding: 5px; border: 1px solid #ccc; font-size: 12px;">
            </div>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">
            <?php if (!empty($post['title'])): ?>
                <h3 class="post-title"><?= htmlspecialchars($post['title'], ENT_QUOTES, 'UTF-8'); ?></h3>
            <?php endif; ?>
            <p class="caption" style="font-size:15px;"><?= htmlspecialchars($post['description'], ENT_QUOTES, 'UTF-8'); ?></p>

            <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">

            <h3 style="margin-left: 10px;">Comments</h3>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">
            <div style="max-height: 400px; overflow-y: auto; margin-bottom: 15px; padding-right: 10px;">
                <?php
                $comments_sql = "SELECT u.username, c.comment_text, c.created_at 
                                 FROM comments c 
                                 JOIN users u ON c.user_id = u.user_id 
                                 WHERE c.post_id = ? 
                                 ORDER BY c.created_at ASC";
                $c_stmt = $conn->prepare($comments_sql);
                $c_stmt->bind_param("i", $post_id);
                $c_stmt->execute();
                $comments_result = $c_stmt->get_result();
                
                if ($comments_result->num_rows > 0):
                    while($c_row = $comments_result->fetch_assoc()): 
                ?>
                        <div class="comment-line" style="margin-bottom: 10px;">
                            <strong><?= htmlspecialchars($c_row['username'], ENT_QUOTES, 'UTF-8'); ?></strong> 
                            <span style="font-size: 11px; color: #999; margin-left: 5px;">
                                <?= date('M j, Y', strtotime($c_row['created_at'])); ?>
                            </span>
                            <br>
                            <?= htmlspecialchars($c_row['comment_text'], ENT_QUOTES, 'UTF-8'); ?>
                        </div>
                <?php 
                    endwhile;
                else:
                    echo "<p style='color:#888; font-size:14px;'>No comments yet. Be the first!</p>";
                endif; 
                ?>
            </div>

            <?php if (isset($_SESSION['user_id'])): ?>
                <?php if (isset($_GET['error']) && $_GET['error'] === 'rate_limit'): ?>
                    <div style="color: red; margin: 10px 0; font-size: 14px; font-weight: bold; background: #ffe6e6; padding: 10px; border-radius: 5px; border: 1px solid #ffcccc; text-align: center; width: 95%; align-self: center;">
                        You are posting comments too fast. Please wait a moment before trying again.
                    </div>
                <?php endif; ?>
    <form action="submit_comments.php" method="POST" class="inline-comment-form">
        <input type="hidden" name="csrf_token" value="<?= generateCSRFToken() ?>">
        <input type="hidden" name="post_id" value="<?= $post['post_id']; ?>"> <input type="text" name="comment_text" placeholder="  Add a comment..." style="width:99%; height:30px;" required>
        <button type="submit" style="width:99%">Post</button>
    </form>
<?php else: ?>
    <div class="inline-comment-form" style="justify-content: center; background: #f9f9f9; padding: 12px; border-radius: 5px; border: 1px solid #eee;">
        <p style="margin: 0; font-size: 14px; color: #555;">
            Want to join the conversation? 
            <a href="login.php" style="color: #007bff; text-decoration: none; font-weight: 600;">Log In here</a>
        </p>
    </div>
    
<?php endif; ?>

        </div>
    </div>
    <br><br><br><br>
</div>


<?php include 'includes/footer.php'; ?>