<?php 
include 'includes/db_connect.php'; 
include 'includes/csrf.php';
include 'includes/header.php'; 

if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'admin') {
    writeSecurityLog('unauthorized_access', "Unauthorized access attempt to admin_dashboard.php", [
        'role' => $_SESSION['role'] ?? 'Guest'
    ]);
    echo "<h2>Access Denied</h2>";
    exit();
}
?>
<div class="content">
<div class="dashboard">
    <h1>Admin Dashboard</h1>
    <table class="dashboard-data">
        <tr class="dash-tr">
            <th>Preview</th>
            <th>Title</th>
            <th>Uploader</th>
            <th>Moderation</th>
            <th>Action</th>
        </tr>
        <?php
        $stmt = $conn->prepare("SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.user_id ORDER BY upload_date DESC");
        $stmt->execute();
        $result = $stmt->get_result();
        $stmt->close();
        while ($row = $result->fetch_assoc()) {
            $escaped_file_name = htmlspecialchars($row['file_name'], ENT_QUOTES, 'UTF-8');
            $escaped_title = htmlspecialchars($row['title'], ENT_QUOTES, 'UTF-8');
            $escaped_username = htmlspecialchars($row['username'], ENT_QUOTES, 'UTF-8');
            $escaped_post_id = htmlspecialchars($row['post_id'], ENT_QUOTES, 'UTF-8');

            // Moderation Status handling
            $mod_status = $row['ai_moderation_status'];
            $mod_score = $row['ai_relevance_score'];
            
            $mod_html = "";
            if ($mod_status === 'Approved') {
                $mod_html = "<span style='background-color: #2e7d32; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;'>Approved (" . htmlspecialchars($mod_score, ENT_QUOTES, 'UTF-8') . "%)</span>";
            } elseif ($mod_status === 'Review') {
                $mod_html = "<span style='background-color: #f57c00; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;'>Review (" . htmlspecialchars($mod_score, ENT_QUOTES, 'UTF-8') . "%)</span>";
            } elseif ($mod_status === 'Flagged') {
                $mod_html = "<span style='background-color: #c62828; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;'>Flagged (" . htmlspecialchars($mod_score, ENT_QUOTES, 'UTF-8') . "%)</span>";
            } else {
                $mod_html = "<span style='color: #888; font-style: italic; font-size: 12px;'>Pending / N/A</span>";
            }

            echo "<tr>";
            echo "<td class='dash-td'>" .(str_starts_with($row['file_type'], 'video/') ? "<video src='uploads/" . $escaped_file_name . "'  style='width: 100px; height: 60px; object-fit: cover; border-radius: 4px;'  muted loop preload='metadata' onmouseover='this.play()' onmouseout='this.pause()'onclick='this.paused ? this.play() : this.pause()'ontouchstart='this.play()'></video>" 
            : "<img src='uploads/" . $escaped_file_name . "'style='width: 100px; height: 60px; object-fit: cover; border-radius: 4px;'loading='lazy'>") . "</td>";
            echo "<td class='dash-td'>" . $escaped_title . "</td>";
            echo "<td class='dash-td'>" . $escaped_username . "</td>";
            echo "<td class='dash-td'>" . $mod_html . "</td>";
            echo "<td class='dash-td'>";

            echo "<form action='delete_post.php' method='POST' style='display:inline; margin-left:5px;' onsubmit=\"return confirm('Delete this post?');\">";
            echo "<input type='hidden' name='id' value='" . $escaped_post_id . "'>";
            echo "<input type='hidden' name='csrf_token' value='" . generateCSRFToken() . "'>";
            echo "<button type='submit' style='background:none; border:none; color:red; cursor:pointer; font-family:inherit; font-size:inherit; padding:0;'>Delete</button>";
            echo "</form>";
            echo "</td>";
            echo "</tr>";
        }
        ?>
    </table>
</div>
</div>
<?php include 'includes/footer.php'; ?>
