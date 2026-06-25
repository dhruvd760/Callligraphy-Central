import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metadata.description_generator import DescriptionGenerator
from response_models import DescriptionResult
from defaults import DESCRIPTION_DEFAULT

@pytest.fixture
def mock_executor():
    return MagicMock()

@pytest.fixture
def generator(mock_executor):
    return DescriptionGenerator(mock_executor)

def test_extract_valid_dict(generator, mock_executor):
    mock_executor.execute_task.return_value = {"description": "A beautiful artwork"}
    result = generator.extract("test")
    assert isinstance(result, DescriptionResult)
    assert result.description == "A beautiful artwork"

def test_extract_invalid_type(generator, mock_executor):
    mock_executor.execute_task.return_value = ["A beautiful artwork"]
    result = generator.extract("test")
    assert result == DESCRIPTION_DEFAULT

def test_extract_none(generator, mock_executor):
    mock_executor.execute_task.return_value = None
    result = generator.extract("test")
    assert result == DESCRIPTION_DEFAULT
