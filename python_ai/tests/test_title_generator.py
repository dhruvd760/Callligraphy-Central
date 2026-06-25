import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metadata.title_generator import TitleGenerator
from response_models import TitleResult
from defaults import TITLE_DEFAULT

@pytest.fixture
def mock_executor():
    return MagicMock()

@pytest.fixture
def generator(mock_executor):
    return TitleGenerator(mock_executor)

def test_extract_valid_dict(generator, mock_executor):
    mock_executor.execute_task.return_value = {"title": "Masterpiece"}
    result = generator.extract("test")
    assert isinstance(result, TitleResult)
    assert result.title == "Masterpiece"

def test_extract_invalid_type(generator, mock_executor):
    mock_executor.execute_task.return_value = ["Masterpiece"]
    result = generator.extract("test")
    assert result == TITLE_DEFAULT

def test_extract_none(generator, mock_executor):
    mock_executor.execute_task.return_value = None
    result = generator.extract("test")
    assert result == TITLE_DEFAULT
