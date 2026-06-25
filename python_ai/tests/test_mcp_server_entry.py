import sys
import json
import io
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_server_entry import main

def test_mcp_server_entry_valid_request(monkeypatch):
    # Mock sys.stdin to simulate an incoming JSON-RPC-like single line payload
    mock_input = json.dumps({"tool": "generate_practice_sheet", "arguments": {}}) + "\n"
    monkeypatch.setattr("sys.stdin", io.StringIO(mock_input))
    
    # Capture sys.stdout
    mock_stdout = io.StringIO()
    monkeypatch.setattr("sys.stdout", mock_stdout)
    
    # Run the entrypoint
    main()
    
    # Verify the output
    output = mock_stdout.getvalue().strip()
    assert output != ""
    
    parsed = json.loads(output)
    assert parsed["status"] == "success"
    assert parsed["tool"] == "generate_practice_sheet"
    assert parsed["result"] == "Dummy practice sheet generation."

def test_mcp_server_entry_invalid_request(monkeypatch):
    mock_input = "not valid json\n"
    monkeypatch.setattr("sys.stdin", io.StringIO(mock_input))
    
    mock_stdout = io.StringIO()
    monkeypatch.setattr("sys.stdout", mock_stdout)
    
    main()
    
    output = mock_stdout.getvalue().strip()
    parsed = json.loads(output)
    assert "error" in parsed
    assert "Expected JSON" in parsed["error"]

def test_mcp_server_entry_missing_tool(monkeypatch):
    mock_input = json.dumps({"tool": "non_existent_tool", "arguments": {}}) + "\n"
    monkeypatch.setattr("sys.stdin", io.StringIO(mock_input))
    
    mock_stdout = io.StringIO()
    monkeypatch.setattr("sys.stdout", mock_stdout)
    
    main()
    
    output = mock_stdout.getvalue().strip()
    parsed = json.loads(output)
    assert "error" in parsed
    assert "not found" in parsed["error"]
