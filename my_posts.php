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
                echo '<div class="card-content">';
                echo '<span class="username">@' . $escaped_username . '</span>';
                echo '<div class="card-header">';
               
                    echo '<span class="username">' . $escaped_title . '</span>';
                    echo '<div class="action-buttons">';
                        echo '<a href="edit_posts.php?id=' . $escaped_post_id . '" class="edit-btn" style="margin-right: 10px;">EDIT</a>';
                        echo '<form action="delete_post.php" method="POST" style="display:inline; margin:0;" onsubmit="return confirm(\'Delete this post?\');">';
                        echo '<input type="hidden" name="id" value="' . $escaped_post_id . '">';
                        echo '<input type="hidden" name="csrf_token" value="' . generateCSRFToken() . '">';
                        echo '<button type="submit" class="delete-btn" style="background:none; cursor:pointer; font-family:inherit; outline:none; display:inline-block; line-height:normal;">DELETE</button>';
                        echo '</form>';
                    echo '</div>';
                echo '</div>';
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