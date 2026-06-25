import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metadata.style_classifier import StyleClassifier
from response_models import StyleResult
from defaults import STYLE_DEFAULT

@pytest.fixture
def mock_executor():
    return MagicMock()

@pytest.fixture
def classifier(mock_executor):
    return StyleClassifier(mock_executor)

def test_extract_valid_dict(classifier, mock_executor):
    mock_executor.execute_task.return_value = {"style": "Copperplate", "confidence": 99, "reason": "Looks like it"}
    result = classifier.extract("test")
    assert isinstance(result, StyleResult)
    assert result.style == "Copperplate"
    assert result.confidence == 99
    assert result.reason == "Looks like it"

def test_extract_partial_dict(classifier, mock_executor):
    mock_executor.execute_task.return_value = {"style": "Copperplate"}
    result = classifier.extract("test")
    assert result.style == "Copperplate"
    assert result.confidence == STYLE_DEFAULT.confidence
    assert result.reason == STYLE_DEFAULT.reason

def test_extract_invalid_type(classifier, mock_executor):
    mock_executor.execute_task.return_value = ["Copperplate"]
    result = classifier.extract("test")
    assert result == STYLE_DEFAULT

def test_extract_none(classifier, mock_executor):
    mock_executor.execute_task.return_value = None
    result = classifier.extract("test")
    assert result == STYLE_DEFAULT
