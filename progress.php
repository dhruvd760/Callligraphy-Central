<?php
include_once 'includes/session_config.php';
include 'includes/db_connect.php';
include 'includes/csrf.php';

// Authentication Check
if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit();
}

$user_id = $_SESSION['user_id'];

// --- 1. DATA RETRIEVAL ---
// Fetch all historical posts for the logged-in user in chronological order
$sql = "SELECT post_id, title, file_name, file_type, ai_score, ai_style, ai_tags, ai_feedback, ai_moderation_status, upload_date 
        FROM posts 
        WHERE user_id = ? 
        ORDER BY upload_date ASC";
$stmt = $conn->prepare($sql);
$stmt->bind_param("i", $user_id);
$stmt->execute();
$result = $stmt->get_result();

$all_posts = [];
$approved_posts = [];
$review_count = 0;

while ($row = $result->fetch_assoc()) {
    $all_posts[] = $row;
    $status = $row['ai_moderation_status'];
    if ($status === 'Approved' || $status === null) {
        $approved_posts[] = $row;
    } elseif ($status === 'Review') {
        $review_count++;
    }
}

$total_uploads = count($all_posts);
$published_count = count($approved_posts);

// --- 2. ADVANCED NLP HEURISTIC ---
// Centralized Skill Map
$skillMap = [
    "spacing" => "Spacing",
    "alignment" => "Alignment",
    "baseline" => "Baseline Alignment",
    "stroke" => "Stroke Consistency",
    "pressure" => "Pressure Control",
    "letter formation" => "Letter Formation",
    "proportion" => "Character Proportion",
    "curve" => "Curves",
    "rhythm" => "Rhythm",
    "contrast" => "Stroke Contrast",
    "hairline" => "Hairlines"
];

$strength_tally = [];
$weakness_tally = [];
foreach ($skillMap as $key => $display) {
    $strength_tally[$display] = 0;
    $weakness_tally[$display] = 0;
}

$highest_score = 0;
$score_sum = 0;
$scored_count = 0;
$scores_array = [];
$first_upload_date = null;
$latest_score = 0;
$first_score = 0;

foreach ($approved_posts as $index => $post) {
    $score = (int)$post['ai_score'];
    if ($score > 0) {
        $score_sum += $score;
        $scored_count++;
        $scores_array[] = $score;
        $latest_score = $score;
        if ($highest_score < $score) $highest_score = $score;
        if ($first_score === 0) $first_score = $score;
    }

    if ($index === 0) {
        $first_upload_date = new DateTime($post['upload_date']);
    }

    // Parse AI Feedback securely
    if (!empty($post['ai_feedback'])) {
        $feedback = json_decode($post['ai_feedback'], true);
        if (json_last_error() === JSON_ERROR_NONE && is_array($feedback)) {
            $improvement = strtolower($feedback['improvement_suggestions'] ?? '');
            $stroke = strtolower($feedback['stroke_analysis'] ?? '');
            $comp = strtolower($feedback['composition_analysis'] ?? '');
            
            foreach ($skillMap as $keyword => $display_name) {
                // Weaknesses are found in improvement_suggestions
                if (strpos($improvement, $keyword) !== false) {
                    $weakness_tally[$display_name]++;
                }
                // Strengths are found in stroke or comp if the score is decent
                if ($score >= 75) {
                    if (strpos($stroke, $keyword) !== false || strpos($comp, $keyword) !== false) {
                        $strength_tally[$display_name]++;
                    }
                }
            }
        }
    }
}

$average_score = $scored_count > 0 ? round($score_sum / $scored_count, 1) : 0;
// Clamp average score between 0 and 100 to prevent rendering issues
$average_score = max(0, min(100, $average_score));
$improvement_since_first = $first_score > 0 ? $latest_score - $first_score : 0;

// Sort strengths and weaknesses
arsort($strength_tally);
arsort($weakness_tally);

$top_strength = null;
foreach ($strength_tally as $skill => $count) {
    if ($count > 0) { $top_strength = $skill; break; }
}

$top_weakness = null;
foreach ($weakness_tally as $skill => $count) {
    if ($count > 0) { $top_weakness = $skill; break; }
}

// --- 3. TREND & CONFIDENCE CALCULATION ---
$trend_status = "Stable";
$trend_icon = "→";
$trend_class = "stable";
$confidence_met = $published_count >= 3;
$recent_avg = 0;
$previous_avg = 0;

if ($confidence_met) {
    // Recent 3 vs prior
    $recent_scores = array_slice($scores_array, -3);
    $previous_scores = array_slice($scores_array, 0, -3);
    
    $recent_avg = count($recent_scores) > 0
    ? array_sum($recent_scores) / count($recent_scores)
    : 0;
    if (count($previous_scores) > 0) {
        $previous_avg = count($previous_scores) > 0
    ? array_sum($previous_scores) / count($previous_scores)
    : 0;
        
        $diff = $recent_avg - $previous_avg;
        if ($diff > 3) {
            $trend_status = "Improving";
            $trend_icon = "↑";
            $trend_class = "improving";
        } elseif ($diff < -3) {
            $trend_status = "Declining";
            $trend_icon = "↓";
            $trend_class = "declining";
        }
    }
}

// --- 4. DYNAMIC SUMMARY GENERATION ---
$summary_paragraphs = [];
if ($total_uploads == 0) {
    $summary_paragraphs[] = "Welcome! You haven't uploaded any artworks yet. Upload more artworks to begin tracking your AI learning progress.";
} elseif (!$confidence_met) {
    $summary_paragraphs[] = "You have uploaded $total_uploads artwork(s) with an average AI score of {$average_score}/100.";
    $summary_paragraphs[] = "More uploads are needed before reliable progress trends can be calculated. Keep practicing and submitting your work!";
} else {
    $summary_paragraphs[] = "You have uploaded $total_uploads artworks, maintaining an overall average AI score of {$average_score}/100.";
    
    if ($trend_status === 'Improving') {
        $summary_paragraphs[] = "Great job! Over your last three uploads, your performance is steadily improving.";
    } elseif ($trend_status === 'Declining') {
        $summary_paragraphs[] = "Your recent scores have decreased slightly compared to your historical average. Don't be discouraged, take your time with your next piece!";
    } else {
        $summary_paragraphs[] = "Your recent scores remain highly consistent.";
    }

    if ($top_strength) {
        $summary_paragraphs[] = "Your strongest area right now is **$top_strength**.";
    }
    
    if ($top_weakness) {
        $summary_paragraphs[] = "**$top_weakness** remains your biggest opportunity for improvement. Keep practicing this to increase your overall AI score.";
    }
}

// Publication Rate
$publication_rate = $total_uploads > 0 ? round(($published_count / $total_uploads) * 100) : 0;

// Uploads per month
$uploads_per_month = 0;
if ($first_upload_date) {
    $now = new DateTime();
    $diff_days = $first_upload_date->diff($now)->days;
    $months = max(1, $diff_days / 30);
    $uploads_per_month = round($total_uploads / $months, 1);
}

// For timeline, get reverse chronological
$timeline_posts = array_reverse($approved_posts);
$recent_timeline = array_slice($timeline_posts, 0, 5); // Last 5

include 'includes/header.php';
?>

<div class="content">
    <h1 style="text-align: center; margin-bottom: 30px;">My AI Progress</h1>

    <?php if ($total_uploads < 2): ?>
        <div class="glass-container" style="text-align: center; margin-bottom: 40px;">
            <h2>Not enough data yet</h2>
            <p style="color: #666; margin-bottom: 20px;">Upload more artworks to begin tracking your AI learning progress and unlock personalized coaching.</p>
            <a href="upload.php" class="upload-action-btn" style="text-decoration: none;">Upload Artwork</a>
        </div>
    <?php endif; ?>

    <!-- AI LEARNING JOURNEY -->
    <div class="glass-container progress-journey-box">
        <h2 style="margin-top: 0; color: #4a3b3b; display: flex; align-items: center; gap: 10px;">
            ✨ AI Learning Journey
        </h2>
        <div style="font-size: 16px; line-height: 1.6; color: #333;">
            <?php foreach ($summary_paragraphs as $para): ?>
                <p><?= htmlspecialchars(str_replace('**', '', $para)) ?></p>
            <?php endforeach; ?>
        </div>
    </div>

    <!-- PROGRESS GAUGES & STATS -->
    <div class="progress-stats-grid">
        
        <!-- Score Gauge -->
        <div class="stat-card progress-gauge-card fade-in delay-1">
            <h3>Avg AI Score</h3>
            <div class="circular-gauge" id="main-gauge" style="--score: 0;" data-target="<?= $average_score ?>">
                <div class="inner-circle">
                    <span class="gauge-value" id="gauge-text">0</span>
                </div>
            </div>
            <p class="gauge-subtext">Out of 100</p>
        </div>

        <!-- Trend Chart Mini -->
        <div class="stat-card fade-in delay-2">
            <h3>Recent Trend</h3>
            <?php if ($confidence_met): ?>
                <div class="trend-indicator <?= $trend_class ?>">
                    <span class="trend-icon"><?= $trend_icon ?></span>
                    <span class="trend-text"><?= $trend_status ?></span>
                </div>
                <div class="mini-bar-chart">
                    <?php 
                    $last5 = array_slice($scores_array, -5);
                    foreach($last5 as $s): 
                        $height = max(10, $s); // Ensure it shows a bit even if low
                    ?>
                        <div class="bar-col" title="Score: <?= $s ?>">
                            <div class="bar-fill trend-bar" data-target="<?= $height ?>" style="height: 0%;"></div>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php else: ?>
                <p style="color: #888; font-size: 14px; margin-top:20px;">Need 3+ uploads</p>
            <?php endif; ?>
        </div>

        <!-- Improvement -->
        <div class="stat-card fade-in delay-3">
            <h3>Improvement</h3>
            <div class="improvement-value <?= $improvement_since_first >= 0 ? 'positive' : 'negative' ?>">
                <?= $improvement_since_first > 0 ? '+' : '' ?><?= $improvement_since_first ?> pts
            </div>
            <p class="gauge-subtext">Since first upload</p>
            
            <h3 style="margin-top: 25px;">Highest Score</h3>
            <div style="font-size: 24px; font-weight: bold; color: #4a3b3b; margin-top: 5px;">
                <?= $highest_score ?>
            </div>
        </div>

        <!-- Meta Stats -->
        <div class="stat-card fade-in delay-3">
            <h3>📊 Portfolio Metrics</h3>
            <ul class="meta-stats-list">
                <li><strong><?= $total_uploads ?></strong> Total Uploads</li>
                <li><strong><?= $published_count ?></strong> Published</li>
                <li><strong><?= $review_count ?></strong> Under Review</li>
                <li><strong><?= $publication_rate ?>%</strong> Approval Rate</li>
                <li><strong><?= $uploads_per_month ?></strong> Uploads / Month</li>
            </ul>
        </div>
    </div>

    <!-- SKILLS BREAKDOWN -->
    <?php if ($published_count > 0): ?>
    <div class="progress-skills-grid">
        <div class="stat-card skills-card strengths fade-in delay-2">
            <h3>💪 Strongest Skills</h3>
            <?php
            $has_strengths = false;
            foreach ($strength_tally as $skill => $count) {
                if ($count > 0) {
                    echo "<div class='skill-item'><span class='check'>✓</span> $skill</div>";
                    $has_strengths = true;
                }
            }
            if (!$has_strengths) {
                echo "<div style='padding: 20px 0;'>
                        <div style='font-size: 30px; margin-bottom: 10px;'>🌱</div>
                        <p class='muted'>Keep practicing to build your core strengths.</p>
                      </div>";
            }
            ?>
        </div>
        <div class="stat-card skills-card weaknesses fade-in delay-2">
            <h3>🎯 Needs Improvement</h3>
            <?php
            $has_weaknesses = false;
            foreach ($weakness_tally as $skill => $count) {
                if ($count > 0) {
                    echo "<div class='skill-item'><span class='target'>↳</span> $skill</div>";
                    $has_weaknesses = true;
                }
            }
            if (!$has_weaknesses) {
                echo "<div style='padding: 20px 0;'>
                        <div style='font-size: 30px; margin-bottom: 10px;'>🌟</div>
                        <p class='muted'>No recurring weaknesses detected!</p>
                      </div>";
            }
            ?>
        </div>
    </div>
    <?php endif; ?>

    <!-- TIMELINE -->
    <?php if (count($recent_timeline) > 0): ?>
    <h2 style="text-align: center; color: #4a3b3b; margin-top: 40px;">⏱️ Recent Activity</h2>
    <div class="timeline-container fade-in delay-3">
        <?php foreach ($recent_timeline as $post): ?>
            <?php
                $s = (int)$post['ai_score'];
                $s_class = 'score-mid';
                if ($s >= 90) $s_class = 'score-high';
                elseif ($s < 70) $s_class = 'score-low';
            ?>
            <div class="timeline-item">
                <div class="timeline-media">
                    <?php if (strpos($post['file_type'], 'image') !== false): ?>
                        <img loading="lazy" src="uploads/<?= htmlspecialchars($post['file_name']) ?>" alt="Thumbnail" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                        <div style="width:100%; height:100%; background:#eee; display:none; align-items:center; justify-content:center; border-radius:8px; font-size: 20px; color: #999;">🖼️</div>
                    <?php else: ?>
                        <div style="width:100%; height:100%; background:#eee; display:flex; align-items:center; justify-content:center; border-radius:8px;">🎥</div>
                    <?php endif; ?>
                </div>
                <div class="timeline-content">
                    <h4><?= htmlspecialchars($post['title']) ?></h4>
                    <span class="timeline-date"><?= date('M j, Y', strtotime($post['upload_date'])) ?></span>
                    <div style="margin-top: 8px;">
                        <span class="timeline-badge score <?= $s_class ?>">Score: <?= htmlspecialchars($post['ai_score']) ?></span>
                        <span class="timeline-badge style"><?= htmlspecialchars($post['ai_style'] ?? 'Unknown Style') ?></span>
                    </div>
                </div>
            </div>
        <?php endforeach; ?>
    </div>
    <?php endif; ?>

</div>

<script>
// Polish animations on page load
window.addEventListener('DOMContentLoaded', () => {
    // Animate Circular Gauge
    const gauge = document.getElementById('main-gauge');
    const gaugeText = document.getElementById('gauge-text');
    if (gauge) {
        const target = parseFloat(gauge.getAttribute('data-target')) || 0;
        let current = 0;
        const duration = 1000;
        const interval = 20;
        const step = target / (duration / interval);
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            gauge.style.setProperty('--score', current);
            gaugeText.textContent = Math.round(current * 10) / 10;
        }, interval);
    }

    // Animate Trend Bars with stagger
    const bars = document.querySelectorAll('.trend-bar');
    bars.forEach((bar, index) => {
        setTimeout(() => {
            bar.style.height = bar.getAttribute('data-target') + '%';
        }, 300 + (index * 150));
    });
});
</script>

<?php include 'includes/footer.php'; ?>
