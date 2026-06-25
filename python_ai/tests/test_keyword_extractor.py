import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metadata.keyword_extractor import KeywordExtractor
from response_models import KeywordResult
from defaults import KEYWORD_DEFAULT

@pytest.fixture
def mock_executor():
    return MagicMock()

@pytest.fixture
def extractor(mock_executor):
    return KeywordExtractor(mock_executor)

def test_extract_valid_list(extractor, mock_executor):
    mock_executor.execute_task.return_value = ["nib", "ink"]
    result = extractor.extract("test")
    assert isinstance(result, KeywordResult)
    assert result.keywords == ["nib", "ink"]

def test_extract_invalid_type(extractor, mock_executor):
    mock_executor.execute_task.return_value = {"keywords": ["nib"]}
    result = extractor.extract("test")
    assert result == KEYWORD_DEFAULT

def test_extract_none(extractor, mock_executor):
    mock_executor.execute_task.return_value = None
    result = extractor.extract("test")
    assert result == KEYWORD_DEFAULT
