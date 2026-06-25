import pytest
import sys
import os
import json
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from workflows.base_workflow import BaseWorkflow
from workflows.workflow_registry import WorkflowRegistry
from workflows.workflow_executor import WorkflowExecutor
from workflows.workflow_agent import WorkflowAgent

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry
from agents.orchestrator import AgentOrchestrator
from memory.context_manager import ContextManager
from adk.adk_adapter import ADKAdapter
from tools.base_tool import BaseTool
from tools.tool_registry import ToolRegistry
from tools.tool_agent import ToolAgent
from prompts.prompt_template import PromptTemplate
from prompts.prompt_registry import PromptRegistry
from prompts.prompt_agent import PromptAgent

# Mock Agents for sequence
class AppendAgentA(BaseAgent):
    @property
    def agent_name(self) -> str:
        return "agent_a"
    def process(self, request: str) -> str:
        return request + " -> A"

class AppendAgentB(BaseAgent):
    @property
    def agent_name(self) -> str:
        return "agent_b"
    def process(self, request: str) -> str:
        return request + " -> B"
        
class ErrorAgent(BaseAgent):
    @property
    def agent_name(self) -> str:
        return "error_agent"
    def process(self, request: str) -> str:
        raise ValueError("Intentional crash")

class MockWorkflow(BaseWorkflow):
    def __init__(self, name, executor, sequence):
        self._name = name
        self.executor = executor
        self.sequence = sequence
        
    @property
    def workflow_name(self) -> str:
        return self._name
        
    def execute(self, request: str) -> Any:
        return self.executor.execute_sequence(request, self.sequence)


def test_base_workflow_contract():
    class InvalidWorkflow(BaseWorkflow):
        pass
    with pytest.raises(TypeError):
        InvalidWorkflow()


def test_workflow_registry():
    registry = WorkflowRegistry()
    wf = MockWorkflow("test_wf", None, [])
    
    registry.register(wf)
    assert registry.list_workflows() == ["test_wf"]
    
    assert registry.get("test_wf") is wf
    assert registry.get("missing") is None


def test_workflow_executor():
    agent_registry = AgentRegistry()
    agent_registry.register(AppendAgentA())
    agent_registry.register(AppendAgentB())
    agent_registry.register(ErrorAgent())
    
    ctx = ContextManager()
    executor = WorkflowExecutor(agent_registry, ctx)
    
    # Sequential chaining
    res = executor.execute_sequence("Start", ["agent_a", "agent_b"])
    assert res == "Start -> A -> B"
    
    # Missing agent safely skipped
    res_skip = executor.execute_sequence("Start", ["agent_a", "missing", "agent_b"])
    assert res_skip == "Start -> A -> B"
    
    # Error handling stops chaining
    res_err = executor.execute_sequence("Start", ["agent_a", "error_agent", "agent_b"])
    assert "error" in res_err
    assert "Intentional crash" in res_err["error"]


def test_workflow_agent():
    agent_registry = AgentRegistry()
    agent_registry.register(AppendAgentA())
    ctx = ContextManager()
    executor = WorkflowExecutor(agent_registry, ctx)
    
    wf = MockWorkflow("my_wf", executor, ["agent_a"])
    wf_registry = WorkflowRegistry()
    wf_registry.register(wf)
    
    wf_agent = WorkflowAgent(wf_registry)
    
    # Valid call
    req = json.dumps({"workflow_name": "my_wf", "request": "Go"})
    res = wf_agent.process(req)
    assert res == {"status": "success", "workflow": "my_wf", "result": "Go -> A"}
    
    # Missing workflow
    req_missing = json.dumps({"workflow_name": "missing", "request": "Go"})
    res_missing = wf_agent.process(req_missing)
    assert res_missing == {"error": "Workflow 'missing' not found."}
    
    # Missing name
    res_no_name = wf_agent.process("{}")
    assert res_no_name == {"error": "No 'workflow_name' provided in request."}
    
    # Invalid JSON
    res_inv = wf_agent.process("not json")
    assert res_inv == {"error": "Invalid workflow request format. Expected JSON."}


def test_workflow_compatibility():
    # Setup full integration environment
    ctx = ContextManager()
    agent_registry = AgentRegistry()
    
    # 1. Tools
    class SimpleTool(BaseTool):
        @property
        def tool_name(self) -> str:
            return "sim_tool"
        def execute(self, **kwargs):
            return "Tool Done"
    tool_reg = ToolRegistry()
    tool_reg.register(SimpleTool())
    tool_agent = ToolAgent(tool_reg, ctx)
    agent_registry.register(tool_agent)
    
    # 2. Prompts
    prompt_reg = PromptRegistry()
    prompt_reg.register(PromptTemplate("sim_prompt", "Prompt Done"))
    prompt_agent = PromptAgent(prompt_reg, ctx)
    agent_registry.register(prompt_agent)
    
    # 3. Dummy Adapter for middle
    class ExtractAgent(BaseAgent):
        @property
        def agent_name(self) -> str:
            return "extractor"
        def process(self, request: str) -> str:
            # Assumes request is JSON string from prompt_agent output
            try:
                data = json.loads(request)
                return json.dumps({"tool_name": "sim_tool", "args": {}})
            except Exception:
                return json.dumps({"tool_name": "sim_tool", "args": {}})
    agent_registry.register(ExtractAgent())
    
    # Executor
    executor = WorkflowExecutor(agent_registry, ctx)
    wf = MockWorkflow("mega_wf", executor, ["prompt_agent", "extractor", "tool_agent"])
    wf_registry = WorkflowRegistry()
    wf_registry.register(wf)
    wf_agent = WorkflowAgent(wf_registry, ctx)
    agent_registry.register(wf_agent)
    
    req = json.dumps({"workflow_name": "mega_wf", "request": json.dumps({"prompt_name": "sim_prompt"})})
    
    # Orchestrator Compatibility
    orchestrator = AgentOrchestrator(agent_registry, ctx)
    res_orch = orchestrator.execute_sequential(req, ["workflow_agent"])
    
    assert res_orch["workflow_agent"]["status"] == "success"
    assert res_orch["workflow_agent"]["result"]["status"] == "success"
    assert res_orch["workflow_agent"]["result"]["result"] == "Tool Done"
    
    # ADKAdapter Compatibility
    adk_adapter = ADKAdapter(agent_registry, ctx)
    adk_wf_agent = adk_adapter.adapt("workflow_agent")
    res_adk = adk_wf_agent.run(req)
    
    assert res_adk["result"]["result"] == "Tool Done"
