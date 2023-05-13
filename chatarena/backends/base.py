from typing import List
from abc import abstractmethod

from ..config import BackendConfig, Configurable
from ..message import Message


class IntelligenceBackend(Configurable):
    """An abstraction of the intelligence source of the agents."""
    stateful = None
    type_name = None

    @abstractmethod
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # registers the arguments with Configurable

    def __init_subclass__(cls, **kwargs):
        # check if the subclass has the required attributes
        for required in ('stateful', 'type_name',):
            if getattr(cls, required) is None:
                raise TypeError(f"Can't instantiate abstract class {cls.__name__} without {required} attribute defined")
        return super().__init_subclass__(**kwargs)

    def to_config(self) -> BackendConfig:
        self._config_dict["backend_type"] = self.type_name
        return BackendConfig(**self._config_dict)

    @abstractmethod
    def query(self, agent_name: str, role_desc: str, history_messages: List[Message], global_prompt: str = None,
              request_msg: Message = None, *args, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    async def async_query(self, agent_name: str, role_desc: str, history_messages: List[Message],
                          global_prompt: str = None, request_msg: Message = None, *args, **kwargs) -> str:
        """Async querying"""
        raise NotImplementedError

    # reset the state of the backend
    def reset(self):
        if self.stateful:
            raise NotImplementedError
        else:
            pass
