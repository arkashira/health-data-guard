import json
from typing import Any, Dict, List, Optional

class Brain:
    """
    Simulates the shared BRAIN (pgvector) context store.
    Uses an in-memory dictionary for this minimal implementation.
    """
    def __init__(self):
        self._memory: Dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        """Stores a context item in the brain."""
        self._memory[key] = value

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieves a context item from the brain."""
        return self._memory.get(key)

    def search(self, query: str) -> List[str]:
        """
        Simulates a vector search by checking if the query string 
        is a substring of stored keys or values (simplified).
        """
        results = []
        for k, v in self._memory.items():
            # Simple string matching simulation
            if query.lower() in str(k).lower() or query.lower() in str(v).lower():
                results.append(k)
        return results

class Agent:
    """
    Base class for an autonomous agent in the chain.
    """
    def __init__(self, name: str, brain: Brain):
        self.name = name
        self.brain = brain

    def execute(self, task: str) -> str:
        """Executes a task and logs to the brain."""
        result = f"{self.name} processed: {task}"
        self.brain.store(f"log_{self.name}", result)
        return result
