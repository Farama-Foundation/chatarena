from typing import List

from ..config import BackendConfig, Configurable
from ..message import Message


class IntelligenceBackend(Configurable):
    """An abstraction of the intelligence source of the agents."""
    stateful = None
    type_name = None

    def __init__(self, config: BackendConfig, *args, **kwargs):
        # Check the backend_type matches the class type_name
        assert config["backend_type"] == self.__class__.type_name

        super().__init__(config=config, *args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        # check if the subclass has the required attributes
        for required in ('stateful', 'type_name',):
            if getattr(cls, required) is None:
                raise TypeError(f"Can't instantiate abstract class {cls.__name__} without {required} attribute defined")
        return super().__init_subclass__(**kwargs)

    def query(self, agent_name: str, role_desc: str, env_desc: str,
              history_messages: List[Message], request_msg: Message = None,
              *args, **kwargs) -> str:
        raise NotImplementedError

    # reset the state of the backend
    def reset(self):
        if self.stateful:
            raise NotImplementedError
        else:
            pass
