from typing import Any
from .base_critic import BaseCritic

class CriticExecutor:
    """Executes a critique against a candidate block."""
    
    def execute_critique(self, candidate: Any, critic: BaseCritic) -> Any:
        try:
            result = critic.evaluate(candidate)
            return {"critique": result}
        except Exception as e:
            return {"error": f"Critic execution failed for '{critic.critic_name}': {str(e)}"}
