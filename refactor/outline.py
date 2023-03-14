import collections


class Arena():
    """
    central module that manages the game environment and players
    """
    def __init__(self, players, moderator):
        pass

    @staticmethod
    def create_from_config(config):
        pass


class Enviornment():
    """
    The environment that the agents interacts with.
    The moderator (if exists) is a special agent that drive the game dynamics
    """
    def __init__(self, moderator_intelligence_source: IntelligenceSource):
        self.moderator = Moderator("moderator", moderator_intelligence_source)

    def step(self, action: str, player: Player) -> (bool, Timestep):
        """
        step function that is called by the agent
        Args:
            action: the action that the agent wants to take
        Returns:
            (valid, timestep)
            valid: whether the action is valid, if the action is not valid the envionment will not proceed
            timestep: the timestep that contains the observation, reward and done
        """
        pass

    def check_action(self, action: str, agent: Agent) -> bool:
        """
        check whether the action is valid
        """
        pass

class Agent():
    def __init__(self, name):
        self.name = name

class Player(Agent):
    """
    Player of the game. It can takes the observation from the environment and return an action
    """
    def __init__(self, name, intelligence_source: IntelligenceSource):
        super(Player, self).__init__(name)
        self.intelligence_source = intelligence_source

    def decide(self, observation: Observation) -> Action:
        """
        decide the action to take
        """
        pass


class Moderator(Agent):
    def __init__(self, name, intelligence_source: IntelligenceSource):
        super(Moderator, self).__init__(name)
        self.intelligence_source = intelligence_source


class IntelligenceSource():
    def query(self, context):
        """
        query the intelligence source given the context
        """
        pass


class Humand(IntelligenceSource):
    pass


class LLM(IntelligenceSource):
    """
    Interface to the language model
    """
    pass


@dataclass
class Timestep():
    observation: Observation
    reward: float
    done: bool

@dataclass
class Action():
    pass

@dataclass
class Observation():
    pass

@dataclass
class Message():
    agent: Agent
    content: str
    timestamp: int = time.time_ns()
    visible_to: Union[None, str, List[Agent]] = "all"

    def get_receivers(self, all_agents: List[Agent]):
        pass

    @property
    def msg_id(self):
        # Generate a unique message id given the content, timestamp and role
        return _hash(f"msg: {self.content}\ntimestamp: {str(self.timestamp)}\nrole: {self.agent.name}")

class MessagePool():
    def __init__(self):
        self._messages = []

    def reset(self):
        self._messages = []

    def append_message(self, message: Message):
        self.message_pool.append(message)

"""
TODOs:
1. Datastorage: online or offline
2. UI: terminal or web gui
3. Detailed design of Action and Observation
"""
