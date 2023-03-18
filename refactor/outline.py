import collections


class Arena():
    """
    central module that manages the game environment and players
    """
    def __init__(self, players: List[Player], environment: Environment):
        self.players = players
        self.environment = environment
        self.message_pool = MessagePool()
        self.current_timestep = self.environment.reset()

    @property
    def num_players(self):
        return len(self.players)

    @property
    def all_agents(self) -> List[Agent]:
        return self.players + [self.moderator]

    @staticmethod
    def create_from_config(config):
        raise NotImplementedError()

    def next_step(self):
        """
        take the action and return the next step
        """
        player = self.environment.get_next_player()
        action = player.decide(self.current_timestep.observation)
        timestep = self.environment.step(action, player)
        self.current_timestep = timestep
        return timestep



@abstract
class Enviornment():
    """
    The environment that the agents interacts with.
    The moderator (if exists) is a special agent that drive the game dynamics
    """
    def __init__(self, moderator_intelligence_source: IntelligenceSource):
        self.moderator = Moderator("moderator", moderator_intelligence_source)

    def get_next_player(self) -> Player:
        """
        get the next player
        """
        pass

    def step(self, action: str, player: Player) -> Timestep:
        """
        step function that is called by the arena
        Args:
            action: the action that the agent wants to take
        Returns:
            timestep: the timestep that contains the observation, reward and done
        """
        pass

    def check_action(self, action: str, agent: Agent) -> bool:
        """
        check whether the action is valid
        """
        pass


class Conversation(Enviornment):
    """
    Fully observable conversation environment.
    Conversation can be either parallel or sequential
    There is a moderator that decides weather the conversation is over according to the public prompts and moderator prompts.
    """
    def __init__(self, moderator_intelligence_source: IntelligenceSource, parallel: bool,
                 max_turns: int, auto_terminate: bool):
        super(Conversation, self).__init__(moderator_intelligence_source)
        self.parallel = parallel
        self.max_turns = max_turns
        self.auto_terminate = auto_terminate


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
        context: the context of the query
        """
        pass


class Humand(IntelligenceSource):
    pass


class ChatGPT(IntelligenceSource):
    """
    Interface to the ChatGPT style model with system, user, assistant roles seperation
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

    def get_visible_messages(self, agent: Agent, turn: int) -> List[Message]:
        """
        get the messages that are visible to the agent before the specified turn
        """
        pass

"""
TODOs:
1. Datastorage: online or offline
2. UI: terminal or web gui
3. Detailed design of Action and Observation
"""
