import openai
import logging
import re
import gradio as gr

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def sys_role_template(system_desc, role_desc):
    return f"{system_desc}\n{role_desc}"


class Agent:
    """Agent class that models general chatbot behavior"""

    def __init__(self, role, system_desc, temperature, max_tokens):
        self.role = role
        self.sys_prompt = [{"role": "system", "content": sys_role_template(system_desc, role)}]
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

    @staticmethod
    def get_components(*args):
        pass

    @staticmethod
    def parse_components(components, name, start_idx):
        pass


class Player(Agent):
    """Player class that models specific player behavior"""

    def __init__(self, name, role, system_desc, temperature, max_tokens):
        self._name = name
        super().__init__(role, system_desc, temperature, max_tokens)

    @property
    def name(self):
        return self._name

    @staticmethod
    def get_components(name):
        role = gr.Textbox(show_label=False, lines=3, visible=True,
                          placeholder=f"Enter the role description for {name}")
        with gr.Accordion(f"{name} Parameters", open=False):
            temperature = gr.Slider(minimum=0, maximum=2.0, value=0.7, step=0.1, interactive=True,
                                    label=f"{name} temperature")
            max_tokens = gr.Slider(minimum=20, maximum=1000, value=300, step=10, interactive=True,
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


DEFAULT_MODERATOR_ROLE = "You are the moderator of the game. You can decide which player speaks next and when to end the conversation."
DEFAULT_NEXT_PLAYER_STRATEGY = f"Which player speak next?"
DEFAULT_END_CRITERIA = "Are players happy to end the conversation? Answer yes or no"


# Moderator: a special type of agent that moderates the conversation, manages who speaks next, and when to end the conversation
class Moderator(Agent):
    """Moderator class that models specific moderator behavior"""

    def __init__(self, role, system_desc, temperature, max_tokens, num_players=2,
                 next_player_strategy=DEFAULT_NEXT_PLAYER_STRATEGY, end_criteria=DEFAULT_END_CRITERIA):
        super().__init__(role, system_desc, temperature, max_tokens)
        self.num_players = num_players
        self.turn = 0
        self.next_player_strategy = next_player_strategy
        self.end_criteria = end_criteria

    @property
    def name(self):
        return "Moderator"

    # @staticmethod
    # def get_default_role(num_players):
    #     return DEFAULT_MODERATOR_ROLE + \
    #         f" There are {str(num_players)} players in the game." \
    #         f" Possible player IDs are {', '.join([str(i + 1) for i in range(num_players)])}."

    def get_response(self, message=None, temperature=0.0, max_tokens=None):
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

    def get_next_player(self):
        # Ask the moderator to decide who speaks next
        try:
            res = self.get_response(self.next_player_strategy, temperature=0.0, max_tokens=5)

            # find the first number in the response and convert it to int
            res = re.search(r"\d+", res).group()
            next_player_idx = int(res.strip())
        except:
            next_player_idx = self.turn % self.num_players
            logger.warning(f"Invalid speaker ID: {res}, resorting to rotary speaker: {next_player_idx}")

        return next_player_idx

    def is_game_end(self, max_turns=100):
        if self.turn >= max_turns:
            return True
        else:
            res = self.get_response(self.end_criteria, temperature=0.0, max_tokens=2)
            if re.match(r"yes|y|yea|yeah|yep|yup|sure|ok|okay|alright", res, re.IGNORECASE):
                logger.warning(f"Decision: {res}. Conversation is ended by moderator after {self.turn} turns.")
                return True
            else:
                return False

    def reset(self):
        self.history = []
        self.turn = 0

    @staticmethod
    def get_components():
        name = "Moderator"
        role = gr.Textbox(show_label=False, lines=2, visible=True,
                          placeholder=f"Enter the role description for {name}")
        with gr.Accordion(f"{name} Advanced Parameters", open=False):
            next_player_strategy = gr.Textbox(show_label=False, lines=2, visible=True,
                                              placeholder="Enter the strategy for deciding who speaks next")
            end_criteria = gr.Textbox(show_label=False, lines=2, visible=True,
                                      placeholder="Enter the end criteria for the conversation")

            temperature = gr.Slider(minimum=0, maximum=2.0, value=0.1, step=0.1, interactive=True,
                                    label=f"{name} temperature")
            max_tokens = gr.Slider(minimum=20, maximum=1000, value=300, step=10, interactive=True,
                                   label=f"{name} max tokens per response")
        return role, next_player_strategy, end_criteria, temperature, max_tokens

    @staticmethod
    def parse_components(components, name, start_idx):
        num_players = components[0]
        system_desc = components[1]
        role = components[start_idx]
        next_player_strategy = components[start_idx + 1]
        end_criteria = components[start_idx + 2]
        temperature = components[start_idx + 3]
        max_tokens = components[start_idx + 4]

        new_moderator = Moderator(role, system_desc, temperature=temperature, max_tokens=max_tokens,
                                  num_players=num_players, next_player_strategy=next_player_strategy,
                                  end_criteria=end_criteria)
        return new_moderator, start_idx + 5
