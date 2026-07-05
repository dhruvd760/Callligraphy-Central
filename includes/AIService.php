<?php
/**
 * AIService
 * Handles all interactions with the Python AI Backend.
 * Encapsulates cURL logic, error handling, validation, and database updates.
 */
class AIService {
    private $apiUrl;
    private $conn;

    public function __construct($conn, $apiUrl = 'http://127.0.0.1:5000/ai') {
        $this->conn = $conn;
        $this->apiUrl = $apiUrl;
    }

    /**
     * Sends an image and metadata to the Python backend for analysis.
     */
    public function evaluatePost($title, $description, $imagePath, $mimeType = 'image/jpeg', $fileName = '', $userId = 0, $postId = 0) {
        $mediaType = strpos($mimeType, 'video/') === 0 ? 'video' : 'image';
        $payloadArray = [
            "task_type" => "evaluate",
            "filters" => [
                "prompt" => "Title: " . $title . "\nDescription: " . $description,
                "image_path" => $imagePath,
                "media_type" => $mediaType,
                "mime_type" => $mimeType,
                "filename" => $fileName,
                "title" => $title,
                "description" => $description,
                "user_id" => $userId,
                "post_id" => $postId
            ]
        ];

        $jsonPayload = json_encode($payloadArray, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);

        $ch = curl_init($this->apiUrl);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonPayload);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'Content-Length: ' . strlen($jsonPayload)
        ]);
        
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 30); 
        curl_setopt($ch, CURLOPT_TIMEOUT, 240);      

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        
        if (curl_errno($ch)) {
            error_log("AI Service Evaluation cURL error: " . curl_error($ch));
            curl_close($ch);
            return null;
        }
        curl_close($ch);

        if ($http_code !== 200) {
            error_log("AI Service Evaluation HTTP error: {$http_code} Response: {$response}");
            return null;
        }

        $ai_json = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            error_log("Invalid JSON from evaluation AI: " . json_last_error_msg());
            return null;
        }

        $validated = [
            'approved' => false,
            'needs_review' => true,
            'relevance_score' => 0,
            'moderation_reason' => '',
            'style' => 'Unknown Style',
            'score' => 0,
            'tags' => '',
            'stroke_analysis' => '',
            'composition_analysis' => '',
            'improvement_suggestions' => ''
        ];

        if (isset($ai_json['approved'])) {
            $validated['approved'] = filter_var($ai_json['approved'], FILTER_VALIDATE_BOOLEAN);
        }
        if (isset($ai_json['needs_review'])) {
            $validated['needs_review'] = filter_var($ai_json['needs_review'], FILTER_VALIDATE_BOOLEAN);
        }

        if (isset($ai_json['relevance_score']) && is_numeric($ai_json['relevance_score'])) {
            $validated['relevance_score'] = max(0, min(100, (int)$ai_json['relevance_score']));
        }
        if (!empty($ai_json['moderation_reason']) && is_string($ai_json['moderation_reason'])) {
            $validated['moderation_reason'] = strip_tags($ai_json['moderation_reason']);
        }
        if (!empty($ai_json['style']) && is_string($ai_json['style'])) {
            $validated['style'] = substr(strip_tags($ai_json['style']), 0, 100);
        }

        if (isset($ai_json['score']) && is_numeric($ai_json['score'])) {
            $validated['score'] = max(0, min(100, (int)$ai_json['score']));
        }

        if (!empty($ai_json['tags'])) {
            if (is_array($ai_json['tags'])) {
                $safe_tags = array_map('strip_tags', $ai_json['tags']);
                $validated['tags'] = substr(implode(', ', $safe_tags), 0, 255);
            } elseif (is_string($ai_json['tags'])) {
                $validated['tags'] = substr(strip_tags($ai_json['tags']), 0, 255);
            }
        }

        if (!empty($ai_json['stroke_analysis']) && is_string($ai_json['stroke_analysis'])) $validated['stroke_analysis'] = strip_tags($ai_json['stroke_analysis']);
        if (!empty($ai_json['composition_analysis']) && is_string($ai_json['composition_analysis'])) $validated['composition_analysis'] = strip_tags($ai_json['composition_analysis']);
        if (!empty($ai_json['improvement_suggestions']) && is_string($ai_json['improvement_suggestions'])) $validated['improvement_suggestions'] = strip_tags($ai_json['improvement_suggestions']);

        return $validated;
    }

    public function analyzePost($title, $description, $imagePath) {
        return $this->evaluatePost($title, $description, $imagePath);
    }

    public function updatePost($postId, $aiData) {
        if (!$aiData) {
            return false;
        }

        $feedback_data = [
            "stroke_analysis" => $aiData['stroke_analysis'],
            "composition_analysis" => $aiData['composition_analysis'],
            "improvement_suggestions" => $aiData['improvement_suggestions']
        ];
        
        $ai_feedback = json_encode($feedback_data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        if ($ai_feedback === false) {
             error_log("Database update failed: Could not encode feedback JSON.");
             return false;
        }

        $stmt = $this->conn->prepare("UPDATE posts SET ai_tags=?, ai_style=?, ai_score=?, ai_feedback=? WHERE post_id=?");
        if (!$stmt) {
             error_log("Database update failed (prepare): " . $this->conn->error);
             return false;
        }

        // Round AI score to nearest 5 for consistency
        $aiData['score'] = (int) round($aiData['score'] / 5) * 5;

        // Keep score within valid range
        $aiData['score'] = max(0, min(100, $aiData['score']));

        $stmt->bind_param("ssisi", 
            $aiData['tags'], 
            $aiData['style'], 
            $aiData['score'], 
            $ai_feedback, 
            $postId
        );
        
        if (!$stmt->execute()) {
            error_log("Database update failed (execute): " . $stmt->error);
            $stmt->close();
            return false;
        }
        
        $affectedRows = $stmt->affected_rows;
        error_log("Database update successful. Post ID: $postId, Affected Rows: $affectedRows");
        
        $stmt->close();
        return true;
    }

    /**
     * Moderates an uploaded image for authenticity.
     */
    public function moderatePost($imagePath) {
        return $this->evaluatePost("", "", $imagePath);
    }

    public function updateModeration($postId, $modData) {
        if (!$modData) return false;

        $status = 'Flagged';
        if ($modData['approved'] === true) $status = 'Approved';
        elseif ($modData['needs_review'] === true) $status = 'Review';

        $stmt = $this->conn->prepare("UPDATE posts SET ai_moderation_status=?, ai_relevance_score=?, ai_moderation_reason=? WHERE post_id=?");
        if (!$stmt) return false;
        
        // s (status), i (relevance_score), s (reason), i (postId) -> sisi
        $stmt->bind_param("sisi", 
            $status, 
            $modData['relevance_score'], 
            $modData['moderation_reason'], 
            $postId
        );
        
        $success = $stmt->execute();
        $stmt->close();
        return $success;
    }
}
?>
