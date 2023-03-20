from typing import List
import re
from time import sleep

from .agent import Player, Moderator
from .backend import OpenAIChat
from .environment import Environment, Conversation, TimeStep, ModeratedConversation

css = """
#col-container {max-width: 90%; margin-left: auto; margin-right: auto; display: flex; flex-direction: column;}
#header {text-align: center;}
#col-chatbox {flex: 1; max-height: min(750px, 100%); display: flex;}
#chatbox {height: min(750px, 100%); max-height: 750px; display:flex;}
#label {font-size: 2em; padding: 0.5em; margin: 0;}
.message {font-size: 1.2em;}
.wrap.svelte-18ha8kq {flex: 1}
.wrap.svelte-18ha8kq.svelte-18ha8kq {max-height: min(700px, 100vh);}
.message-wrap {max-height: min(700px, 100vh);}
"""


class Arena():
    """
    Utility class that manages the game environment and players
    """

    def __init__(self, players: List[Player], environment: Environment):
        self.players = players
        self.environment = environment
        self.current_timestep = self.environment.reset()
        self._name2player = {player.name: player for player in self.players}

    @property
    def num_players(self):
        return len(self.players)

    def step(self) -> TimeStep:
        """
        Take a step in the game: one player takes an action and the environment updates
        """
        player_name = self.environment.get_next_player()
        player = self._name2player[player_name]  # get the player object
        observation = self.environment.get_observation(player_name)  # get the observation for the player
        action = player(observation)  # take an action
        timestep = self.environment.step(player_name, action)  # update the environment
        return timestep

    def run(self, num_steps: int = 1):
        """
        run the game for num_turns
        """
        for i in range(num_steps):
            timestep = self.step()
            if timestep.terminal:
                break

    @staticmethod
    def from_config(config):
        env_config = config["environment"]

        players = []
        for player_idx, player_config in enumerate(config["players"]):
            player = Player(
                name=f"Player {player_idx + 1}",
                role_desc=player_config["role_desc"],
                env_desc=env_config["env_desc"],
                backend=OpenAIChat(
                    temperature=player_config["temperature"],
                    max_tokens=player_config["max_tokens"],
                    model_name=player_config["model_name"],
                )
            )
            players.append(player)

        if env_config.get("moderator", None) is not None:
            env = ModeratedConversation(
                player_names=[player.name for player in players],
                env_desc=env_config["env_desc"],
                parallel=env_config["parallel"],
                moderator=Moderator(
                    role_desc=env_config["moderator"]["role_desc"],
                    env_desc=env_config["env_desc"],
                    backend=OpenAIChat(
                        temperature=env_config["moderator"]["temperature"],
                        max_tokens=env_config["moderator"]["max_tokens"],
                        model_name=env_config["moderator"]["model_name"],
                    ),
                    terminal_condition=env_config["moderator"]["terminal_condition"],
                ),
                moderator_visibility=env_config["moderator"]["visibility"],
            )
        else:
            env = Conversation(
                player_names=[player.name for player in players],
                env_desc=env_config["env_desc"],
                parallel=env_config["parallel"],
            )
        return Arena(players, env)

    @staticmethod
    def save_config(config):
        raise NotImplementedError()

    def launch_webapp(self):
        import gradio as gr

        def play_game(*args):
            # Clear the chatbot UI output and hide the other components
            yield gr.update(value=[], visible=True), gr.update(value="Running...", interactive=False)

            env_desc, max_steps, parallel = args[:3]

            offset = 3
            if isinstance(self.environment, ModeratedConversation):
                moderator, offset = Moderator.parse_components(args, start_idx=offset)

            players = []
            for player_id in range(1, len(self.players) + 1):
                player, offset = Player.parse_components(args, f"Player {player_id}", start_idx=offset)
                players.append(player)

            # Create the arena to manage the game environment
            if isinstance(self.environment, ModeratedConversation):
                arena = Arena(
                    players,
                    environment=ModeratedConversation(
                        player_names=[player.name for player in players],
                        env_desc=env_desc,
                        parallel=parallel,
                        moderator=moderator,
                        moderator_visibility="all")
                )
            else:
                arena = Arena(
                    players,
                    environment=Conversation(
                        player_names=[player.name for player in players],
                        env_desc=env_desc,
                        parallel=parallel)
                )

            def _convert_to_chatbot_output(all_messages):
                chatbot_output = []
                for i, message in enumerate(all_messages):
                    agent_name, msg = message.agent_name, message.content
                    new_msg = re.sub(r'\n+', '<br>', msg.strip())  # Preprocess message for chatbot output
                    new_msg = f"**[{agent_name}]**: {new_msg}"  # Add role to the message

                    if agent_name == "Moderator":
                        chatbot_output.append((new_msg, None))
                    else:
                        chatbot_output.append((None, new_msg))
                return chatbot_output

            # Main loop: Play the game
            for turn in range(max_steps):
                try:
                    timestep = arena.step()
                    arena.environment.print()
                    all_messages = timestep.observation  # user sees what the moderator sees
                    chatbot_output = _convert_to_chatbot_output(all_messages)
                    # Update the chatbot UI output
                    yield chatbot_output, gr.update()
                    sleep(0.2)

                    if timestep.terminal:
                        break
                except Exception as e:
                    print(e)

            yield gr.update(), gr.update(value="Run", interactive=True)

        with gr.Blocks(css=css) as demo:
            with gr.Column(elem_id="col-container"):
                gr.Markdown("""# 🏟 Chat Arena️<br>
                Prompting chat-based AI agents to play games in a language-driven environment. 
                [Arena Tutorial](https://example.com)""",
                            elem_id="header")

                with gr.Row():
                    with gr.Column(elem_id="col-chatbox"):
                        chatbot = gr.Chatbot(elem_id="chatbox", visible=True, label="Chat Arena")

                    with gr.Column(elem_id="col-config"):
                        all_components = []  # keep track of all components so we can use them later
                        with gr.Accordion("Game Configuration", open=False):
                            gr.Markdown("Scenario/Rule Description")
                            system_desc = gr.Textbox(show_label=False, lines=3,
                                                     label="System Description",
                                                     placeholder="Enter a description of a scenario or the game rules.",
                                                     visible=True,
                                                     value=self.environment.env_desc)
                            max_steps = gr.Slider(minimum=4, maximum=32, value=8, step=1, interactive=True,
                                                  label="Max steps per game")

                            with gr.Accordion("Advanced Configuration", open=False):
                                parallel = gr.Checkbox(label="Parallel Actions", value=False, visible=True)
                                # All game-level metadata
                                all_components += [system_desc, max_steps, parallel]

                                if isinstance(self.environment, ModeratedConversation):
                                    with gr.Accordion("Moderator Configuration", open=False):
                                        moderator_components = self.environment.moderator.get_components()
                                        all_components.extend(moderator_components)

                        for player_idx in range(len(self.players)):
                            with gr.Accordion(f"Player {player_idx + 1}", open=True):
                                player_components = self.players[player_idx].get_components()
                                all_components.extend(player_components)

                        with gr.Row():
                            btn_run = gr.Button("Run")

            btn_run.click(play_game, all_components, [chatbot, btn_run])

        demo.queue()
        demo.launch(debug=True)
