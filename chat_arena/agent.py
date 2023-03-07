import openai
import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



def role_template(context, role_desc):
    return f"You are playing a game. Here is the scenario or game rules: {context}\n Here's your role description: {role_desc}."


class Agent:
    """Agent class that models general chatbot behavior"""

    def __init__(self, role, context, temperature, max_tokens):
        self.role = role
        self.sys_prompt = [{"role": "system", "content": role_template(context, role)}]
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.history = []

    def get_response(self, message=None, temperature=None, max_tokens=None):
        if message is not None:
            self.history.append({"role": "user", "content": message})
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.sys_prompt + self.history,
            temperature=temperature, max_tokens=max_tokens)

        response = completion.choices[0]['message']['content']
        self.history.append({"role": "assistant", "content": response})
        return response

    def add_message(self, message, role="user"):
        self.history.append({"role": role, "content": message})

    def reset(self):
        self.history = []


class Player(Agent):
    """Player class that models specific player behavior"""

    def __init__(self, player_id, role, context, temperature, max_tokens):
        self.player_id = player_id
        # role = f"You are {self.name}. " + role
        super().__init__(role, context, temperature, max_tokens)

    @property
    def name(self):
        return f"Player {self.player_id}"


DEFAULT_MODERATOR_ROLE = "You are the moderator of the game. You can decide which player speaks next and when to end the conversation."


# Moderator: a special type of agent that moderates the conversation, manages who speaks next, and when to end the conversation
class Moderator(Agent):
    """Moderator class that models specific moderator behavior"""

    @staticmethod
    def get_default_role(num_players):
        return DEFAULT_MODERATOR_ROLE + \
            f" There are {str(num_players)} players in the game." \
            f" Possible player IDs are {', '.join([str(i + 1) for i in range(num_players)])}."

    def __init__(self, role, context, temperature, max_tokens, num_players, max_turns):
        super().__init__(role, context, temperature, max_tokens)
        self.num_players = num_players
        self.turn = 0
        self.max_turns = max_turns

    @property
    def name(self):
        return "Moderator"

    def get_response(self, message=None, temperature=None, max_tokens=None):
        self.history.append({"role": "user", "content": message})

        if message is None:
            raise ValueError("Message cannot be None")
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.sys_prompt + self.history,
            temperature=temperature, max_tokens=max_tokens)

        response = completion.choices[0]['message']['content']
        self.history.append({"role": "assistant", "content": response})
        return response

    def get_next_speaker(self, rotary_speaker=False):
        if rotary_speaker:
            next_speaker = self.turn % self.num_players
        else:
            # Ask the moderator to decide who speaks next
            res = self.get_response(
                f"Who should speaks next, Player {', '.join([str(i + 1) for i in range(self.num_players - 1)])} or {str(self.num_players)}?",
                temperature=0.0, max_tokens=5)
            try:
                # find the first number in the response and convert it to int
                res = re.search(r"\d+", res).group()
                next_speaker = int(res.strip())
            except:
                next_speaker = self.turn % self.num_players
                logger.warning(f"Invalid speaker ID: {res}, resorting to rotary speaker: {next_speaker}")

        self.turn += 1
        return next_speaker

    def is_conversation_over(self):
        if self.turn >= self.max_turns:
            return True
        else:
            res = self.get_response("Should the game be terminated? Yes or No", temperature=0.0, max_tokens=2)
            if re.match(r"yes|y|yea|yeah|yep|yup|sure|ok|okay|alright", res, re.IGNORECASE):
                logger.warning(f"Decision: {res}. Conversation is ended by moderator after {self.turn} turns.")
                return True
            else:
                return False

    def reset(self):
        self.history = []
        self.turn = 0
