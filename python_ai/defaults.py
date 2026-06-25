from response_models import (
    TagResult, KeywordResult, StyleResult, 
    LanguageResult, DescriptionResult, TitleResult
)

TAG_DEFAULT = TagResult(tags=["calligraphy"])

KEYWORD_DEFAULT = KeywordResult(keywords=["keyword"])

STYLE_DEFAULT = StyleResult(
    style="Unknown", 
    confidence=0, 
    reason="fallback"
)

LANGUAGE_DEFAULT = LanguageResult(language="Unknown Language")

DESCRIPTION_DEFAULT = DescriptionResult(description="No description available.")

TITLE_DEFAULT = TitleResult(title="Untitled Calligraphy")
