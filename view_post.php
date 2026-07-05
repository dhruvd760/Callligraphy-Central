<?php
include_once 'includes/session_config.php';
include 'includes/db_connect.php';
include 'includes/csrf.php';
include 'includes/header.php';

// Check if an ID was passed in the URL
if (!isset($_GET['id']) || empty($_GET['id'])) {
    echo "<div class='content'><h2>Post not found.</h2><a href='gallery.php'>Return to Gallery</a></div>";
    include 'includes/footer.php';
    exit();
}

$post_id = intval($_GET['id']);

$is_admin = isset($_SESSION['role']) && $_SESSION['role'] === 'admin';
$mod_condition = $is_admin ? "" : "AND (posts.ai_moderation_status = 'Approved' OR posts.ai_moderation_status IS NULL)";

// Fetch the specific post using a prepared statement
$sql = "SELECT posts.*, users.username, 
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count 
        FROM posts 
        JOIN users ON posts.user_id = users.user_id 
        WHERE posts.post_id = ? " . $mod_condition;
$stmt = $conn->prepare($sql);
$stmt->bind_param("i", $post_id);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows == 0) {
    echo "<div class='content'><h2>Post not found.</h2><a href='gallery.php'>Return to Gallery</a></div>";
    include 'includes/footer.php';
    exit();
}

$post = $result->fetch_assoc();
?>

<div class="content" style="display: flex; flex-direction: column; align-items: center; justify-content: flex-start; min-height: 80vh;">

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
                <input type="text" value="http://<?= htmlspecialchars($_SERVER['HTTP_HOST'], ENT_QUOTES, 'UTF-8') . htmlspecialchars(dirname($_SERVER['PHP_SELF']), ENT_QUOTES, 'UTF-8'); ?>/view_post.php?id=<?= htmlspecialchars($post['post_id'], ENT_QUOTES, 'UTF-8'); ?>" readonly style="width: 90%; padding: 5px; border: 1px solid #ccc; font-size: 12px; box-sizing: border-box;">
            </div>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">
            <?php if (!empty($post['title'])): ?>
                <h3 class="post-title"><?= htmlspecialchars($post['title'], ENT_QUOTES, 'UTF-8'); ?></h3>
            <?php endif; ?>
            <p class="caption" style="font-size:15px;"><?= htmlspecialchars($post['description'], ENT_QUOTES, 'UTF-8'); ?></p>

            <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">

            <div style="background: #fdfdfd; border: 1px solid #e0e0e0; border-radius: 8px; margin: 15px 10px; padding: 15px;">
                <h3 style="margin-top: 0; color: #b71c1c; font-size: 16px; border-bottom: 1px solid #eee; padding-bottom: 5px;">AI Calligraphy Analysis</h3>
                <?php if (!empty($post['ai_style']) || !empty($post['ai_score'])): ?>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div><strong>Style:</strong> <?= htmlspecialchars($post['ai_style'] ?? 'Unknown', ENT_QUOTES, 'UTF-8'); ?></div>
                        <div><strong>Score:</strong> <span style="background: #b71c1c; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;"><?= htmlspecialchars($post['ai_score'] ?? 'N/A', ENT_QUOTES, 'UTF-8'); ?>/100</span></div>
                    </div>
                    <?php if (!empty($post['ai_description'])): ?>
                        <p style="font-size: 14px; color: #444; margin-bottom: 10px;"><em>"<?= htmlspecialchars($post['ai_description'], ENT_QUOTES, 'UTF-8'); ?>"</em></p>
                    <?php endif; ?>
                    
                    <?php 
                    if (!empty($post['ai_feedback'])) {
                        $feedback = json_decode($post['ai_feedback'], true);
                        if (is_array($feedback)) {
                            echo "<div style='font-size: 13px; color: #555; line-height: 1.5;'>";
                            if (!empty($feedback['stroke_analysis'])) {
                                echo "<strong>Strokes:</strong> " . htmlspecialchars($feedback['stroke_analysis'], ENT_QUOTES, 'UTF-8') . "<br>";
                            }
                            if (!empty($feedback['composition'])) {
                                echo "<strong>Composition:</strong> " . htmlspecialchars($feedback['composition'], ENT_QUOTES, 'UTF-8') . "<br>";
                            }
                            if (!empty($feedback['improvement_suggestions'])) {
                                echo "<strong>Suggestions:</strong> " . htmlspecialchars($feedback['improvement_suggestions'], ENT_QUOTES, 'UTF-8') . "<br>";
                            }
                            echo "</div>";
                        }
                    }
                    ?>
                    
                    <?php if (!empty($post['ai_tags'])): ?>
                        <div style="margin-top: 10px;">
                            <?php 
                            $tags = explode(',', $post['ai_tags']);
                            foreach ($tags as $tag): 
                                $tag = trim($tag);
                                if (!empty($tag)):
                            ?>
                                <span style="display: inline-block; background: #eee; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 5px; color: #666;">#<?= htmlspecialchars($tag, ENT_QUOTES, 'UTF-8'); ?></span>
                            <?php 
                                endif;
                            endforeach; 
                            ?>
                        </div>
                    <?php endif; ?>
                <?php else: ?>
                    <p style="font-size: 14px; color: #888; font-style: italic; margin: 0; text-align: center;">AI temporarily unavailable</p>
                <?php endif; ?>
            </div>

            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">

            <!-- AI-Powered Recommendation System -->
            <div style="margin: 0 10px; width: calc(100% - 20px);">
                <h3 style="color: #4a3b3b; font-size: 18px; margin-bottom: 15px;">Similar Artworks</h3>
                
                <?php
                // Get current post's AI attributes for matching
                $current_style = $post['ai_style'] ?? '';
                $current_score = isset($post['ai_score']) ? (int)$post['ai_score'] : 0;
                
                // Extract first tag for fuzzy tag matching
                $first_tag_like = '%impossible_tag_match%';
                if (!empty($post['ai_tags'])) {
                    $tags_arr = explode(',', $post['ai_tags']);
                    if (count($tags_arr) > 0) {
                        $first_tag_like = '%' . trim($tags_arr[0]) . '%';
                    }
                }

                // Query priority: 1) Exact style match, 2) Tag match, 3) Closest score diff
                // We exclude the current post using post_id != ?
                $rec_sql = "SELECT post_id, file_name, file_type, title, ai_style, ai_score,
                                   (CASE WHEN ai_style = ? THEN 1 ELSE 0 END) AS style_match,
                                   (CASE WHEN ai_tags LIKE ? THEN 1 ELSE 0 END) AS tag_match
                            FROM posts
                            WHERE post_id != ?
                            ORDER BY style_match DESC, tag_match DESC, ABS(IFNULL(ai_score, 0) - ?) ASC
                            LIMIT 4";
                
                $rec_stmt = $conn->prepare($rec_sql);
                // Bind: s (style), s (first_tag), i (post_id), i (score)
                $rec_stmt->bind_param("ssii", $current_style, $first_tag_like, $post_id, $current_score);
                $rec_stmt->execute();
                $rec_result = $rec_stmt->get_result();
                
                if ($rec_result->num_rows > 0):
                ?>
                    <div class="insta-grid ai-rec-grid">
                        <?php while($rec = $rec_result->fetch_assoc()): ?>
                            <div class="insta-card" style="margin: 0; width: 100%;">
                                <div class="card-media">
                                    <?php if (str_starts_with($rec['file_type'], 'image/')): ?>
                                        <img src="uploads/<?= htmlspecialchars($rec['file_name'], ENT_QUOTES, 'UTF-8'); ?>" alt="Artwork preview" style="max-width: 100%; height: auto; display: block;">
                                    <?php else: ?>
                                        <video style="max-width: 100%; height: auto; display: block;">
                                            <source src="uploads/<?= htmlspecialchars($rec['file_name'], ENT_QUOTES, 'UTF-8'); ?>" type="<?= htmlspecialchars($rec['file_type'], ENT_QUOTES, 'UTF-8'); ?>">
                                        </video>
                                    <?php endif; ?>
                                </div>
                                <div class="card-content" style="padding: 10px;">
                                    <?php if (!empty($rec['title'])): ?>
                                        <h4 style="margin: 0 0 5px 0; font-size: 14px; color: #333; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                            <?= htmlspecialchars($rec['title'], ENT_QUOTES, 'UTF-8'); ?>
                                        </h4>
                                    <?php endif; ?>
                                    
                                    <div style="font-size: 12px; margin-bottom: 10px; display: flex; flex-wrap: wrap; gap: 5px;">
                                        <?php if (!empty($rec['ai_style'])): ?>
                                            <span style="background: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 4px;">
                                                <?= htmlspecialchars($rec['ai_style'], ENT_QUOTES, 'UTF-8'); ?>
                                            </span>
                                        <?php endif; ?>
                                        <?php if (!empty($rec['ai_score'])): ?>
                                            <span style="background: #e8f5e9; color: #2e7d32; padding: 2px 6px; border-radius: 4px; font-weight: bold;">
                                                Score: <?= htmlspecialchars($rec['ai_score'], ENT_QUOTES, 'UTF-8'); ?>/100
                                            </span>
                                        <?php endif; ?>
                                    </div>
                                    
                                    <a href="view_post.php?id=<?= htmlspecialchars($rec['post_id'], ENT_QUOTES, 'UTF-8'); ?>" class="ai-rec-btn" style="display: block; text-align: center; background: #4a3b3b; color: white; text-decoration: none; padding: 6px 0; border-radius: 4px; font-size: 13px; font-weight: bold; transition: background 0.2s;">
                                        View Artwork
                                    </a>
                                </div>
                            </div>
                        <?php endwhile; ?>
                    </div>
                <?php else: ?>
                    <p style="font-size: 14px; color: #888; font-style: italic;">No similar artworks found yet.</p>
                <?php endif; ?>
            </div>

            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">

            <h3 style="margin-left: 10px;">Comments</h3>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">
            <div style="max-height: 400px; overflow-y: auto; margin-bottom: 15px; padding-right: 10px;">
                <?php
                $comments_per_page = 50;
                $c_page = isset($_GET['c_page']) && is_numeric($_GET['c_page']) ? (int)$_GET['c_page'] : 1;
                if ($c_page < 1) $c_page = 1;
                $c_offset = ($c_page - 1) * $comments_per_page;

                $comments_sql = "SELECT u.username, c.comment_text, c.created_at 
                                 FROM comments c 
                                 JOIN users u ON c.user_id = u.user_id 
                                 WHERE c.post_id = ? 
                                 ORDER BY c.created_at ASC LIMIT ? OFFSET ?";
                $c_stmt = $conn->prepare($comments_sql);
                $c_stmt->bind_param("iii", $post_id, $comments_per_page, $c_offset);
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
                
                <!-- Comments Pagination Controls -->
                <div style="text-align: center; margin-top: 10px;">
                    <?php if ($c_page > 1): ?>
                        <a href="?id=<?= $post_id ?>&c_page=<?= $c_page - 1 ?>" style="font-size: 12px; color: #007bff; text-decoration: none; margin-right: 15px;">⬅ Previous</a>
                    <?php endif; ?>
                    
                    <?php if ($comments_result->num_rows == $comments_per_page): ?>
                        <a href="?id=<?= $post_id ?>&c_page=<?= $c_page + 1 ?>" style="font-size: 12px; color: #007bff; text-decoration: none;">Next ➡</a>
                    <?php endif; ?>
                </div>
            </div>

            <?php if (isset($_SESSION['user_id'])): ?>
                <?php if (isset($_GET['error']) && $_GET['error'] === 'rate_limit'): ?>
                    <div style="color: red; margin: 10px 0; font-size: 14px; font-weight: bold; background: #ffe6e6; padding: 10px; border-radius: 5px; border: 1px solid #ffcccc; text-align: center; width: 95%; align-self: center;">
                        You are posting comments too fast. Please wait a moment before trying again.
                    </div>
                <?php endif; ?>
    <form action="submit_comments.php" method="POST" class="inline-comment-form">
        <input type="hidden" name="csrf_token" value="<?= generateCSRFToken() ?>">
        <input type="hidden" name="post_id" value="<?= $post['post_id']; ?>"> <input type="text" name="comment_text" placeholder="  Add a comment..." style="width:99%; height:30px; box-sizing: border-box;" required>
        <button type="submit" style="width:99%">Post</button>
    </form>
<?php else: ?>
    <div class="inline-comment-form" style="justify-content: flex-start; background: #f9f9f9; padding: 12px; border-radius: 5px; border: 1px solid #eee;">
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