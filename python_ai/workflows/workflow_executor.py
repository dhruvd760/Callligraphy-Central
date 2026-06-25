import sys
import os
import json
from typing import List, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.agent_registry import AgentRegistry
from memory.context_manager import ContextManager

class WorkflowExecutor:
    """Executes a defined sequence of agents where the output of one feeds into the next."""
    
    def __init__(self, agent_registry: AgentRegistry, context_manager: ContextManager):
        self.agent_registry = agent_registry
        self.context_manager = context_manager

    def execute_sequence(self, request: str, agent_names: List[str]) -> Any:
        """
        Sequential execution where the output of one agent becomes the input to the next.
        Missing agents are safely skipped.
        """
        current_input = request
        
        for name in agent_names:
            agent = self.agent_registry.get(name)
            if agent is None:
                continue
            
            # Ensure the input to the agent is a string, as required by BaseAgent.process(request: str)
            if not isinstance(current_input, str):
                current_input = json.dumps(current_input)
                
            try:
                result = agent.process(current_input)
                current_input = result
            except Exception as e:
                return {"error": f"Workflow execution failed at agent '{name}': {str(e)}"}
                
        return current_input
