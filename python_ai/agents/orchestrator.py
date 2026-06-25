from typing import List, Dict, Any
from .agent_registry import AgentRegistry
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory.context_manager import ContextManager

class AgentOrchestrator:
    """
    Top-level Orchestrator for sequentially delegating tasks to agents.
    """
    def __init__(self, registry: AgentRegistry, context_manager: ContextManager):
        self.registry = registry
        self.context_manager = context_manager

    def execute_sequential(self, request: str, agent_names: List[str]) -> Dict[str, Any]:
        """
        Iterates over agent_names, retrieves each from the registry, invokes process(),
        and aggregates responses.
        """
        aggregated_responses = {}
        
        for name in agent_names:
            agent = self.registry.get(name)
            if agent is not None:
                try:
                    response = agent.process(request)
                    aggregated_responses[name] = response
                except Exception as e:
                    aggregated_responses[name] = {"error": f"Agent {name} crashed: {str(e)}"}
            else:
                aggregated_responses[name] = {"error": "Agent not found."}
                
        return aggregated_responses
