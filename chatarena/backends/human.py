from .base import IntelligenceBackend
from ..config import BackendConfig


# An Error class for the human backend
class HumanBackendError(Exception):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        super().__init__(f"Human backend requires a UI to get input from {agent_name}.")


class Human(IntelligenceBackend):
    stateful = False
    type_name = "human"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_config(self) -> BackendConfig:
        return BackendConfig(backend_type=self.type_name)

    def query(self, agent_name: str, **kwargs) -> str:
        raise HumanBackendError(agent_name)
