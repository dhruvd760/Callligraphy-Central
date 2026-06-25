# AI Architecture for Calligraphy Central

This document details the responsibilities, workflows, and communication patterns of the new AI layer for Calligraphy Central. This setup strictly adheres to the principle of maintaining the existing PHP/MySQL frontend while offloading AI processing to an independent Python layer.

## Overview and Separation of Concerns

The Calligraphy Central application is divided into two distinct components:
1.  **Frontend/Data Layer (PHP & MySQL)**: Manages authentication, sessions, database interactions, core UI rendering, and basic rate-limiting/security.
2.  **AI Layer (Python)**: Operates entirely independently as a background service or API. It is solely responsible for intelligent processing, content generation, search enhancement, and moderation.

The PHP codebase does not directly interface with the Gemini API; all such calls are managed by the Python Orchestrator to ensure token efficiency, context management, and single responsibility.

## Communication Patterns

*   **Protocol**: RESTful HTTP API (e.g., via Flask or FastAPI).
*   **Flow**: 
    1.  The PHP application (e.g., `upload.php`) makes an asynchronous or synchronous HTTP POST request to the Python AI service (`app.py`).
    2.  `app.py` receives the payload (containing `user_id`, `post_id`, raw text, or image paths) and passes it to the `Orchestrator`.
    3.  The `Orchestrator` delegates the task to the appropriate agent(s).
    4.  The Python layer returns a JSON response containing the generated insights, tags, or moderation flags.
    5.  The PHP application parses the JSON and stores the result in MySQL (e.g., in a new `ai_metadata` table).

## Orchestration Workflows

The `Orchestrator` is the central traffic controller. Example workflow for a new post:
1.  **Ingestion**: `app.py` receives a "new_post" event.
2.  **Moderation**: `Orchestrator` calls `ModerationAgent` to check for safety. If flagged, returns an immediate block to PHP.
3.  **Tagging**: `Orchestrator` calls `MetadataAgent` to extract semantic tags.
4.  **Feedback**: `Orchestrator` calls `MentorAgent` to generate an educational critique.
5.  **Curation**: `Orchestrator` assesses if the post meets the threshold for the `CuratorAgent`.

## Agent Responsibilities

*   **MetadataAgent**: Extracts, tags, and structures metadata from uploaded calligraphy posts.
*   **SearchAgent**: Provides semantic and structured search capabilities across user and post data.
*   **RecommendationAgent**: Processes user preferences and historical interactions to suggest relevant posts and mentors.
*   **MentorAgent**: Handles generative feedback, offering critique and improvement tips for calligraphy works.
*   **ModerationAgent**: Scans text and image content for policy violations, spam, or abusive behavior.
*   **CuratorAgent**: Selects high-quality posts to feature on the homepage or discover sections.
*   **NotificationAgent**: Formats and triggers personalized insights or alerts for users.

## Graceful Failure Handling

To maintain a seamless user experience if the AI layer fails or experiences high latency:
*   **Non-Blocking AI**: The PHP application treats the AI API as an optional enhancement. If a request times out (e.g., after 3 seconds) or fails, the core action (e.g., uploading a post) still completes successfully.
*   **Fallback mechanisms**: Missing AI tags simply won't display. Search will revert to basic MySQL `LIKE` queries if the semantic `SearchAgent` is unreachable.
*   **Circuit Breaker**: The PHP layer will temporarily halt requests to the Python API if multiple consecutive errors occur, preventing bottlenecks.

## Token Efficiency Principles

*   **Caching**: `Orchestrator` will cache identical queries (especially for `SearchAgent`).
*   **Prompt Truncation**: Inputs to the Gemini models will be strictly truncated and summarized to avoid hitting context window limits.
*   **Batching**: `NotificationAgent` and `CuratorAgent` will operate on batch cron jobs rather than per-event triggers where possible, minimizing redundant prompt context.
