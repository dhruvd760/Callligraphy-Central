import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock gemini_client module before importing MetadataAgent to prevent google.generativeai import error
sys.modules['gemini_client'] = MagicMock()

from metadata_agent import MetadataAgent
from response_models import TagResult, KeywordResult, StyleResult, LanguageResult, DescriptionResult, TitleResult

@pytest.fixture
def mock_gemini():
    with patch('metadata_agent.GeminiClient') as MockClient:
        yield MockClient()

@pytest.fixture
def agent(mock_gemini):
    return MetadataAgent()

def test_extract_title(agent):
    with patch.object(agent.title_generator, 'extract') as mock_extract:
        mock_extract.return_value = TitleResult(title="Test Title")
        assert agent.extract_title(text_description="test") == "Test Title"

def test_extract_style_wrapper(agent):
    with patch.object(agent.style_classifier, 'extract') as mock_extract:
        mock_extract.return_value = StyleResult(style="Copperplate", confidence=90, reason="Test")
        assert agent.extract_style(text_description="test") == "Copperplate"

def test_extract_language(agent):
    with patch.object(agent.language_detector, 'extract') as mock_extract:
        mock_extract.return_value = LanguageResult(language="English")
        assert agent.extract_language(text_description="test") == "English"

def test_generate_tags(agent):
    with patch.object(agent.tag_extractor, 'extract') as mock_extract:
        mock_extract.return_value = TagResult(tags=["a", "b"])
        assert agent.generate_tags(text_description="test") == ["a", "b"]

def test_analyze_post(agent):
    with patch.object(agent, 'extract_title', return_value="Title"), \
         patch.object(agent, 'extract_style', return_value="Style"), \
         patch.object(agent, 'extract_language', return_value="Lang"), \
         patch.object(agent, 'generate_tags', return_value=["t1"]), \
         patch.object(agent, 'generate_description', return_value={"description": "Desc"}):
        result = agent.analyze_post(text_description="test")
        assert result["title"] == "Title"
        assert result["style"] == "Style"
        assert result["language"] == "Lang"
        assert result["tags"] == ["t1"]
        assert result["description"] == "Desc"
        assert result["difficulty"] == "Beginner"

def test_generate_metadata_success(agent):
    with patch.object(agent.tag_extractor, 'extract', return_value=TagResult(tags=["t"])), \
         patch.object(agent.keyword_extractor, 'extract', return_value=KeywordResult(keywords=["k"])), \
         patch.object(agent.style_classifier, 'extract', return_value=StyleResult(style="S", confidence=1, reason="R")), \
         patch.object(agent.description_generator, 'extract', return_value=DescriptionResult(description="D")):
        
        result = agent.generate_metadata("test")
        assert result["tags"] == ["t"]
        assert result["keywords"] == ["k"]
        assert result["style"]["style"] == "S"
        assert result["description"]["description"] == "D"

def test_generate_metadata_failure_propagation(agent):
    with patch.object(agent.tag_extractor, 'extract', side_effect=Exception("Failed")):
        result = agent.generate_metadata("test")
        assert result["tags"] == ["calligraphy"]
        assert result["style"]["style"] == "Unknown"

def test_process_metadata_success(agent):
    with patch.object(agent, 'generate_metadata', return_value={"a": 1}):
        result = agent.process_metadata("test")
        assert result["status"] == "success"
        assert result["metadata"] == {"a": 1}

def test_process_metadata_failure(agent):
    with patch.object(agent, 'generate_metadata', side_effect=Exception("Failed")):
        result = agent.process_metadata("test")
        assert result["status"] == "error"
        assert result["metadata"] == {}

def test_analyze_post_failure(agent):
    with patch.object(agent, 'extract_title', side_effect=Exception("Failed")):
        result = agent.analyze_post("test")
        assert result["title"] == "Error Processing Post"
