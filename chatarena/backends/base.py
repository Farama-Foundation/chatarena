from typing import List
from abc import abstractmethod

from ..config import BackendConfig, Configurable
from ..message import Message


class IntelligenceBackend(Configurable):
    """An abstraction of the intelligence source of the agents."""
    stateful = None
    type_name = None

    def __init_subclass__(cls, **kwargs):
        # check if the subclass has the required attributes
        for required in ('stateful', 'type_name',):
            if getattr(cls, required) is None:
                raise TypeError(f"Can't instantiate abstract class {cls.__name__} without {required} attribute defined")
        return super().__init_subclass__(**kwargs)

    @abstractmethod
    def query(self, agent_name: str, prompt: str, history_messages: List[Message], global_prompt: str = None,
              request_msg: Message = None, *args, **kwargs) -> str:
        raise NotImplementedError

    # reset the state of the backend
    def reset(self):
        if self.stateful:
            raise NotImplementedError
        else:
            pass
