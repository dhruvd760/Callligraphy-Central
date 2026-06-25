import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.gemini_task_executor import GeminiTaskExecutor

@pytest.fixture
def mock_client():
    return MagicMock()

@pytest.fixture
def executor(mock_client):
    return GeminiTaskExecutor(mock_client)

def test_execute_task_success(executor, mock_client):
    mock_client.generate_response.return_value = '{"test": "data"}'
    result = executor.execute_task("System", "Prompt")
    assert result == {"test": "data"}

def test_execute_task_no_client():
    executor = GeminiTaskExecutor(None)
    assert executor.execute_task("System", "Prompt") is None

def test_execute_task_exception(executor, mock_client):
    mock_client.generate_response.side_effect = Exception("API Error")
    assert executor.execute_task("System", "Prompt") is None

def test_parse_json_valid_json(executor):
    assert executor._parse_json('{"key": "value"}') == {"key": "value"}
    assert executor._parse_json('["a", "b", "c"]') == ["a", "b", "c"]
    assert executor._parse_json('{"style": {"name": "Copperplate"}}') == {"style": {"name": "Copperplate"}}

def test_parse_json_markdown_fences(executor):
    assert executor._parse_json('```json\n{"key": "value"}\n```') == {"key": "value"}
    assert executor._parse_json('```\n{"key": "value"}\n```') == {"key": "value"}

def test_parse_json_whitespace(executor):
    assert executor._parse_json('   {"key": "value"}   ') == {"key": "value"}

def test_parse_json_invalid(executor):
    assert executor._parse_json("") is None
    assert executor._parse_json("    ") is None
    assert executor._parse_json("```json\n\n```") is None
    assert executor._parse_json("{invalid: json}") is None

def test_execute_task_caching(executor, mock_client):
    mock_client.generate_response.return_value = '{"test": "data"}'
    
    # First call
    result1 = executor.execute_task("System", "Prompt")
    
    # Second call (identical)
    result2 = executor.execute_task("System", "Prompt")
    
    # Verify results are identical
    assert result1 == {"test": "data"}
    assert result2 == {"test": "data"}
    
    # Verify the underlying gemini_client was only called once
    mock_client.generate_response.assert_called_once()
