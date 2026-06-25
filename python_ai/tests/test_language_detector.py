import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metadata.language_detector import LanguageDetector
from response_models import LanguageResult
from defaults import LANGUAGE_DEFAULT

@pytest.fixture
def mock_executor():
    return MagicMock()

@pytest.fixture
def detector(mock_executor):
    return LanguageDetector(mock_executor)

def test_extract_valid_dict(detector, mock_executor):
    mock_executor.execute_task.return_value = {"language": "French"}
    result = detector.extract("test")
    assert isinstance(result, LanguageResult)
    assert result.language == "French"

def test_extract_invalid_type(detector, mock_executor):
    mock_executor.execute_task.return_value = ["French"]
    result = detector.extract("test")
    assert result == LANGUAGE_DEFAULT

def test_extract_none(detector, mock_executor):
    mock_executor.execute_task.return_value = None
    result = detector.extract("test")
    assert result == LANGUAGE_DEFAULT
