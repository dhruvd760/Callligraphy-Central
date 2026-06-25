import pytest
import sys
import os
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.tool_registry import MCPToolRegistry
from mcp.mcp_tools import (
    AnalyzeCalligraphyTool,
    GeneratePracticeSheetTool,
    EvaluateSubmissionTool,
    SearchStylesTool,
    SaveSessionTool,
    LoadSessionTool
)

def test_analyze_calligraphy_tool():
    tool = AnalyzeCalligraphyTool()
    assert tool.tool_name == "analyze_calligraphy"
    res = tool.execute(data="test")
    assert res == {
        "status": "success",
        "tool": "analyze_calligraphy",
        "result": "Dummy analysis."
    }

def test_generate_practice_sheet_tool():
    tool = GeneratePracticeSheetTool()
    assert tool.tool_name == "generate_practice_sheet"
    res = tool.execute(style="copperplate")
    assert res == "Dummy practice sheet generation."

def test_evaluate_submission_tool():
    tool = EvaluateSubmissionTool()
    assert tool.tool_name == "evaluate_submission"
    res = tool.execute(submission_id="123")
    assert res == "Dummy evaluation."

def test_search_styles_tool():
    tool = SearchStylesTool()
    assert tool.tool_name == "search_styles"
    res = tool.execute(query="gothic")
    assert res == "Dummy search results."

def test_save_session_tool():
    tool = SaveSessionTool()
    assert tool.tool_name == "save_session"
    res = tool.execute(session_data={})
    assert res == "Dummy session saved."

def test_load_session_tool():
    tool = LoadSessionTool()
    assert tool.tool_name == "load_session"
    res = tool.execute(session_id="abc")
    assert res == "Dummy session loaded."

def test_mcp_tool_registration():
    registry = MCPToolRegistry()
    
    tools = [
        AnalyzeCalligraphyTool(),
        GeneratePracticeSheetTool(),
        EvaluateSubmissionTool(),
        SearchStylesTool(),
        SaveSessionTool(),
        LoadSessionTool()
    ]
    
    for tool in tools:
        registry.register(tool)
        
    registered_tools = registry.list_tools()
    
    assert "analyze_calligraphy" in registered_tools
    assert "generate_practice_sheet" in registered_tools
    assert "evaluate_submission" in registered_tools
    assert "search_styles" in registered_tools
    assert "save_session" in registered_tools
    assert "load_session" in registered_tools
    
    assert len(registered_tools) == 6
