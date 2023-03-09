import openai
import logging
import re
import gradio as gr

from .base import Agent
from .message import Message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

EOS = ("<EOS>", "_EOS_", "#EOS", "(EOS)")  # End of sentence token


class Player(Agent):
    """Player class that models specific player behavior"""

    def __init__(self, name, role, system_desc, temperature, max_tokens):
        self._name = name
        super().__init__(role, system_desc, temperature, max_tokens)

    @property
    def name(self):
        return self._name

    def get_response(self, history, temperature=None, max_tokens=None, stop=EOS):
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.sys_prompt + history,
            temperature=temperature, max_tokens=max_tokens,
            stop=stop)

        response = completion.choices[0]['message']['content'].strip()

        # Seems like there is a bug with stop sequence. Remove trailing _ < # ( tokens
        if response.endswith("_") or response.endswith("<") or response.endswith("#") or response.endswith("("):
            response = response[:-1]

        return response.strip()

    @staticmethod
    def get_components(name):
        with gr.Column():
            role = gr.Textbox(show_label=False, lines=3, visible=True,
                              placeholder=f"Enter the role description for {name}")
            with gr.Accordion(f"{name} Parameters", open=False):
                temperature = gr.Slider(minimum=0, maximum=2.0, value=0.7, step=0.1, interactive=True,
                                        label=f"{name} temperature")
                max_tokens = gr.Slider(minimum=10, maximum=500, value=100, step=10, interactive=True,
                                       label=f"{name} max tokens per response")

        return role, temperature, max_tokens

    @staticmethod
    def parse_components(components, name, start_idx):
        role = components[start_idx]
        system_desc = components[1]
        temperature = components[start_idx + 1]
        max_tokens = components[start_idx + 2]
        new_player = Player(name, role, system_desc, temperature, max_tokens)
        return new_player, start_idx + 3

    def step(self, arena, turn: int) -> Message:
        # Get the visible history from arena
        visible_history = arena.get_visible_history(self, turn=turn)

        # Preprocess the visible history
        for i, message in enumerate(visible_history):
            if message.role == self:
                visible_history[i] = {"role": "assistant", "content": message.content}
            else:
                if arena.num_players == 2:
                    visible_history[i] = {"role": "user", "content": message.content}
                else:
                    # If there are more than 2 players, we need to distinguish between the players
                    visible_history[i] = {"role": "user", "content": f"[{message.role.name}]: {message.content}"}

        response = self.get_response(visible_history)
        message = Message(self, response, turn=turn, visible_to="all")  # broadcast the response to all players
        return message


DEFAULT_MODERATOR_ROLE = "You are the moderator of the game. You can decide which player speaks next and when to end the conversation."
DEFAULT_NEXT_PLAYER_PROMPT = "Who speaks next?"
DEFAULT_END_CRITERIA = "Are players happy to end the conversation? Answer yes or no"


def next_player_func(prompt, players):
    return f"{prompt} Choices: " + "\n".join([f"({i + 1}) {p.name}" for i, p in enumerate(players)])


# Moderator: a special type of agent that moderates the conversation, manages who speaks next, and when to end the conversation
class Moderator(Agent):
    """Moderator class that models specific moderator behavior"""

    def __init__(self, role, system_desc, temperature, max_tokens, num_players=2,
                 next_player_prompt=DEFAULT_NEXT_PLAYER_PROMPT, end_criteria=DEFAULT_END_CRITERIA):
        super().__init__(role, system_desc, temperature, max_tokens)
        self.num_players = num_players
        self.next_player_prompt = next_player_prompt
        self.end_criteria = end_criteria

    @property
    def name(self):
        return "Moderator"

    def get_response(self, history, temperature=None, max_tokens=None, stop=EOS):
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.sys_prompt + history,
            temperature=temperature, max_tokens=max_tokens, stop=stop)

        response = completion.choices[0]['message']['content']
        return response

    @staticmethod
    def get_components():
        name = "Moderator"
        role = gr.Textbox(show_label=False, lines=2, visible=True,
                          placeholder=f"Enter the role description for {name}",
                          value=DEFAULT_MODERATOR_ROLE)
        with gr.Accordion(f"{name} Advanced Parameters", open=False):
            next_player_prompt = gr.Textbox(show_label=False, lines=2, visible=True,
                                            placeholder="Enter the strategy for deciding who speaks next",
                                            value=DEFAULT_NEXT_PLAYER_PROMPT)
            end_criteria = gr.Textbox(show_label=False, lines=2, visible=True,
                                      placeholder="Enter the end criteria for the conversation",
                                      value=DEFAULT_END_CRITERIA)

            temperature = gr.Slider(minimum=0, maximum=2.0, value=0.0, step=0.1, interactive=True,
                                    label=f"{name} temperature")
            max_tokens = gr.Slider(minimum=20, maximum=1000, value=20, step=10, interactive=True,
                                   label=f"{name} max tokens per response")
        return role, next_player_prompt, end_criteria, temperature, max_tokens

    @staticmethod
    def parse_components(components, name, start_idx):
        num_players = components[0]
        system_desc = components[1]
        role = components[start_idx]
        next_player_prompt = components[start_idx + 1]
        end_criteria = components[start_idx + 2]
        temperature = components[start_idx + 3]
        max_tokens = components[start_idx + 4]

        new_moderator = Moderator(role, system_desc, temperature=temperature, max_tokens=max_tokens,
                                  num_players=num_players, next_player_prompt=next_player_prompt,
                                  end_criteria=end_criteria)
        return new_moderator, start_idx + 5

    def step(self, arena, turn: int) -> Message:
        # Get the visible history from arena
        visible_history = arena.get_visible_history(self, turn=turn)

        # Preprocess the visible history
        for i, message in enumerate(visible_history):
            if message.role == self:
                visible_history[i] = {"role": "assistant", "content": message.content}
            else:
                # Since there are more than one player, we need to distinguish between the players
                visible_history[i] = {"role": "user", "content": f"[{message.role.name}]: {message.content}"}

        response = self.get_response(visible_history)

        message = Message(self, response, turn=turn, visible_to=None)  # Moderator does not broadcast the response
        return message

    def get_next_player(self, arena):
        visible_history = arena.get_visible_history(self)  # turn=None means get the entire history
        # Preprocess the visible history
        for i, message in enumerate(visible_history):
            if message.role == self:
                visible_history[i] = {"role": "assistant", "content": message.content}
            else:
                # Since there are more than one player, we need to distinguish between the players
                visible_history[i] = {"role": "user", "content": f"[{message.role.name}]: {message.content}"}

        players = arena.players
        query = {"role": "system", "content": next_player_func(self.next_player_prompt, players)}

        # Ask the moderator to decide who speaks next
        try:
            res = self.get_response(visible_history + [query], temperature=0.0, max_tokens=5)
            res = re.search(r"\d+", res).group()  # find the first number in the response and convert it to int
            next_player_idx = int(res.strip()) - 1  # convert to 0-based index
        except Exception as e:
            print(e)
            next_player_idx = None
            logger.warning(f"Moderator failed to decide who speaks next.")

        return next_player_idx

    def is_terminal(self, arena):
        visible_history = arena.get_visible_history(self)  # turn=None means get the entire history
        # Preprocess the visible history
        for i, message in enumerate(visible_history):
            if message.role == self:
                visible_history[i] = {"role": "assistant", "content": message.content}
            else:
                # Since there are more than one player, we need to distinguish between the players
                visible_history[i] = {"role": "user", "content": f"[{message.role.name}]: {message.content}"}

        query = {"role": "system", "content": self.end_criteria}

        res = self.get_response(visible_history + [query], temperature=0.0, max_tokens=2)
        if re.match(r"yes|y|yea|yeah|yep|yup|sure|ok|okay|alright", res, re.IGNORECASE):
            logger.warning(f"Decision: {res}. Conversation is ended by moderator.")
            return True
        else:
            return False
