import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metadata.tag_extractor import TagExtractor
from response_models import TagResult
from defaults import TAG_DEFAULT

@pytest.fixture
def mock_executor():
    return MagicMock()

@pytest.fixture
def extractor(mock_executor):
    return TagExtractor(mock_executor)

def test_extract_valid_list(extractor, mock_executor):
    mock_executor.execute_task.return_value = ["calligraphy", "art"]
    result = extractor.extract("test")
    assert isinstance(result, TagResult)
    assert result.tags == ["calligraphy", "art"]

def test_extract_invalid_type(extractor, mock_executor):
    mock_executor.execute_task.return_value = {"tags": ["calligraphy"]}
    result = extractor.extract("test")
    assert result == TAG_DEFAULT

def test_extract_none(extractor, mock_executor):
    mock_executor.execute_task.return_value = None
    result = extractor.extract("test")
    assert result == TAG_DEFAULT
