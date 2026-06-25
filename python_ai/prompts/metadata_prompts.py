SYSTEM_INSTRUCTION = (
    "You are an expert metadata specialist for Calligraphy Central.\n"
    "Generate concise, educational, beginner-friendly metadata.\n"
    "Return structured JSON only.\n"
    "Classify calligraphy styles, extract searchable tags, educational keywords, and helpful descriptions."
)

PROMPT_TAGS = (
    "Generate a list of searchable tags for the following calligraphy post: '{text}'. "
    "Respond ONLY with a JSON array of string tags. Example output: "
    "[\"copperplate\", \"flourishing\", \"practice\", \"beginner\"]"
)

PROMPT_KEYWORDS = (
    "Extract educational and technical calligraphy keywords (such as script names, nib types, "
    "stroke terminology, materials, or learning vocab) from: '{text}'. "
    "Respond ONLY with a JSON array of string keywords."
)

PROMPT_STYLE = (
    "Classify the calligraphy style/script referenced in the text: '{text}'. "
    "Respond ONLY with a JSON object in this format:\n"
    "{{\n"
    "  \"style\": \"StyleName\",\n"
    "  \"confidence\": 95,\n"
    "  \"reason\": \"Detailed reason for classification.\"\n"
    "}}"
)

PROMPT_DESCRIPTION = (
    "Produce a concise, beginner-friendly description summarizing the work described: '{text}'. "
    "Respond ONLY with a JSON object in this format:\n"
    "{{\n"
    "  \"description\": \"Your generated description text here.\"\n"
    "}}"
)

PROMPT_TITLE = (
    "Extract or generate a suitable, short title for this calligraphy post description: '{text}'. "
    "Respond ONLY with a JSON object containing a 'title' string attribute."
)

PROMPT_LANGUAGE = (
    "Detect the primary language of this text/description: '{text}'. "
    "Respond ONLY with a JSON object containing a 'language' string attribute."
)
