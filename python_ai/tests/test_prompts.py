import pytest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from prompts.base_prompt import BasePrompt
from prompts.prompt_template import PromptTemplate
from prompts.prompt_registry import PromptRegistry
from prompts.prompt_agent import PromptAgent
from agents.orchestrator import AgentOrchestrator
from agents.agent_registry import AgentRegistry
from memory.context_manager import ContextManager
from adk.adk_adapter import ADKAdapter

def test_base_prompt_contract():
    class InvalidPrompt(BasePrompt):
        pass
    with pytest.raises(TypeError):
        InvalidPrompt()

def test_prompt_template_and_registry():
    registry = PromptRegistry()
    tmpl = PromptTemplate("greeting", "Hello, {name}!")
    
    registry.register(tmpl)
    assert registry.list_prompts() == ["greeting"]
    
    retrieved = registry.get("greeting")
    assert retrieved is tmpl
    assert retrieved.render(name="World") == "Hello, World!"
    
    missing = registry.get("missing")
    assert missing is None

def test_prompt_agent():
    registry = PromptRegistry()
    registry.register(PromptTemplate("greet", "Hi {user}"))
    agent = PromptAgent(registry)
    
    # Valid call
    req = json.dumps({"prompt_name": "greet", "args": {"user": "Alice"}})
    res = agent.process(req)
    assert res == {"status": "success", "prompt": "greet", "rendered": "Hi Alice"}
    
    # Missing prompt
    req_missing = json.dumps({"prompt_name": "missing"})
    res_missing = agent.process(req_missing)
    assert res_missing == {"error": "Prompt 'missing' not found."}
    
    # Invalid JSON
    res_invalid = agent.process("not json")
    assert res_invalid == {"error": "Invalid prompt request format. Expected JSON."}
    
    # Missing prompt_name
    res_no_name = agent.process("{}")
    assert res_no_name == {"error": "No 'prompt_name' provided in request."}
    
    # Missing formatting arguments
    req_bad_args = json.dumps({"prompt_name": "greet", "args": {}})
    res_bad_args = agent.process(req_bad_args)
    assert "error" in res_bad_args
    assert "Missing formatting argument" in res_bad_args["error"]

def test_prompt_agent_compatibility():
    prompt_registry = PromptRegistry()
    prompt_registry.register(PromptTemplate("test", "Test: {msg}"))
    
    prompt_agent = PromptAgent(prompt_registry)
    agent_registry = AgentRegistry()
    agent_registry.register(prompt_agent)
    
    context_manager = ContextManager()
    
    # Test Orchestrator
    orchestrator = AgentOrchestrator(agent_registry, context_manager)
    req = json.dumps({"prompt_name": "test", "args": {"msg": "ok"}})
    res_orch = orchestrator.execute_sequential(req, ["prompt_agent"])
    assert res_orch["prompt_agent"]["rendered"] == "Test: ok"
    
    # Test ADKAdapter
    adapter = ADKAdapter(agent_registry, context_manager)
    adk_agent = adapter.adapt("prompt_agent")
    res_adk = adk_agent.run(req)
    assert res_adk["rendered"] == "Test: ok"
