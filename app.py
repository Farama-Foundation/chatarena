import gradio as gr

# from chat_arena.agent import Player, Moderator
# from chat_arena.arena import Arena
# from chat_arena.environment import Environment, Conversation, TimeStep, ModeratedConversation
from chat_arena.backend import BACKEND_REGISTRY
from chat_arena.environment import ENV_REGISTRY

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

DEFAULT_BACKEND = "openai-chat"
MAX_NUM_PLAYERS = 6
DEFAULT_NUM_PLAYERS = 2


def get_moderator_components():
    name = "Moderator"
    with gr.Row():
        with gr.Column():
            role_desc = gr.Textbox(label="Moderator role", lines=1, visible=False, interactive=True,
                                   placeholder=f"Enter the role description for {name}")
            terminal_condition = gr.Textbox(show_label=False, lines=1, visible=False, interactive=True,
                                            placeholder="Enter the end criteria for the conversation")
        with gr.Column():
            backend_type = gr.Dropdown(show_label=False, visible=False, interactive=True,
                                       choices=list(BACKEND_REGISTRY.keys()), value=DEFAULT_BACKEND)
            with gr.Accordion(f"{name} Parameters", open=False, visible=False) as accordion:
                temperature = gr.Slider(minimum=0, maximum=2.0, step=0.1, interactive=True, visible=False,
                                        label=f"temperature", value=0.7)
                max_tokens = gr.Slider(minimum=10, maximum=500, step=10, interactive=True, visible=False,
                                       label=f"max tokens", value=200)

    return [role_desc, terminal_condition, backend_type, accordion, temperature, max_tokens]


def get_player_components(name, visible):
    with gr.Row():
        with gr.Column():
            role_desc = gr.Textbox(label=name, lines=3, interactive=True, visible=visible,
                                   placeholder=f"Enter the role description for {name}")
        with gr.Column():
            backend_type = gr.Dropdown(show_label=False, choices=list(BACKEND_REGISTRY.keys()),
                                       interactive=True, visible=visible, value=DEFAULT_BACKEND)
            with gr.Accordion(f"{name} Parameters", open=False, visible=visible) as accordion:
                temperature = gr.Slider(minimum=0, maximum=2.0, step=0.1, interactive=True, visible=visible,
                                        label=f"temperature", value=0.7)
                max_tokens = gr.Slider(minimum=10, maximum=500, step=10, interactive=True, visible=visible,
                                       label=f"max tokens", value=200)

    return [role_desc, backend_type, accordion, temperature, max_tokens]


"""Launch the gradio UI"""

with gr.Blocks(css=css) as demo:
    state = gr.State()

    with gr.Column(elem_id="col-container"):
        gr.Markdown("""# 🏟 Chat Arena️<br>
Prompting chat-based AI agents to play games in a language-driven environment. 
[Arena Tutorial](https://chat.ai-arena.org/tutorial)""",
                    elem_id="header")

        # Environment configuration
        with gr.Row():
            gr.Markdown("Environment Configuration")
            env_selector = gr.Dropdown(choices=list(ENV_REGISTRY.keys()), label="Environment Type", show_label=False)
        env_desc = gr.Textbox(show_label=False, lines=2, visible=True, label="System Description",
                              placeholder="Enter a description of a scenario or the game rules.")
        with gr.Row():
            parallel = gr.Checkbox(label="Parallel Actions", value=False, visible=True)
            moderator_enabled = gr.Checkbox(label="Enable Moderator", value=False, visible=True)

        env_components = [env_desc, parallel]
        with gr.Column():
            moderator_components = get_moderator_components()


        # Update the visibility of moderator components based on the moderator_enabled checkbox
        def _update_moderator_components(enabled):
            return {comp: gr.update(visible=enabled) for comp in moderator_components}


        moderator_enabled.change(_update_moderator_components, moderator_enabled, moderator_components)

        with gr.Row():
            with gr.Column(elem_id="col-chatbox"):
                chatbot = gr.Chatbot(elem_id="chatbox", visible=True, label="Chat Arena")

            with gr.Column(elem_id="col-config"):  # Player Configuration
                # gr.Markdown("Player Configuration")

                all_players_components, players_idx2comp = [], {}
                with gr.Blocks():
                    num_player_slider = gr.Slider(2, MAX_NUM_PLAYERS, value=DEFAULT_NUM_PLAYERS, step=1,
                                                  label="Number of players:")
                    for i in range(MAX_NUM_PLAYERS):
                        player_name = f"Player {i + 1}"
                        with gr.Tab(player_name, visible=(i < DEFAULT_NUM_PLAYERS)) as tab:
                            player_comps = get_player_components(player_name, visible=(i < DEFAULT_NUM_PLAYERS))

                        players_idx2comp[i] = player_comps + [tab]
                        all_players_components += player_comps + [tab]


                def variable_players(k):
                    k = int(k)
                    update_dict = {}
                    for i in range(MAX_NUM_PLAYERS):
                        if i < k:
                            for comp in players_idx2comp[i]:
                                update_dict[comp] = gr.update(visible=True)
                        else:
                            for comp in players_idx2comp[i]:
                                update_dict[comp] = gr.update(visible=False)
                    return update_dict


                num_player_slider.change(variable_players, num_player_slider, all_players_components)

                # for player_idx in range(len(config["players"])):
                #     with gr.Accordion(f"Player {player_idx + 1}", open=True):
                #         player_config = config["players"][player_idx]
                #         player_components = Player.get_components(player_config)
                #         all_components.extend(player_components)

                human_input = gr.Textbox(show_label=False, lines=1, visible=True,
                                         placeholder="Human Player Input: ")
                with gr.Row():
                    btn_step = gr.Button("Step")
                    btn_restart = gr.Button("Restart")

    # def play_game(*args):
    #     # Clear the chatbot UI output and hide the other components
    #     yield gr.update(value=[], visible=True), gr.update(value="Running...", interactive=False)
    #
    #     env_desc, max_steps, parallel = args[:3]
    #
    #     offset = 3
    #     if isinstance(arena.environment, ModeratedConversation):
    #         moderator, offset = Moderator.parse_components(args, start_idx=offset)
    #
    #     players = []
    #     for player_id in range(1, len(arena.players) + 1):
    #         player, offset = Player.parse_components(args, f"Player {player_id}", start_idx=offset)
    #         players.append(player)
    #
    #     # Create the arena to manage the game environment
    #     if isinstance(arena.environment, ModeratedConversation):
    #         arena = Arena(
    #             players,
    #             environment=ModeratedConversation(
    #                 player_names=[player.name for player in players],
    #                 env_desc=env_desc,
    #                 parallel=parallel,
    #                 moderator=moderator,
    #                 moderator_visibility="all")
    #         )
    #     else:
    #         arena = Arena(
    #             players,
    #             environment=Conversation(
    #                 player_names=[player.name for player in players],
    #                 env_desc=env_desc,
    #                 parallel=parallel)
    #         )
    #
    #     def _convert_to_chatbot_output(all_messages):
    #         chatbot_output = []
    #         for i, message in enumerate(all_messages):
    #             agent_name, msg = message.agent_name, message.content
    #             new_msg = re.sub(r'\n+', '<br>', msg.strip())  # Preprocess message for chatbot output
    #             new_msg = f"**[{agent_name}]**: {new_msg}"  # Add role to the message
    #
    #             if agent_name == "Moderator":
    #                 chatbot_output.append((new_msg, None))
    #             else:
    #                 chatbot_output.append((None, new_msg))
    #         return chatbot_output
    #
    #     # Main loop: Play the game
    #     for turn in range(max_steps):
    #         try:
    #             timestep = arena.step()
    #             arena.environment.print()
    #             all_messages = timestep.observation  # user sees what the moderator sees
    #             chatbot_output = _convert_to_chatbot_output(all_messages)
    #             # Update the chatbot UI output
    #             yield chatbot_output, gr.update()
    #             sleep(0.2)
    #
    #             if timestep.terminal:
    #                 break
    #         except Exception as e:
    #             print(e)
    #
    #     yield gr.update(), gr.update(value="Run", interactive=True)
    #
    # btn_run.click(play_game, all_components, [chatbot, btn_run])

demo.queue()
# demo.launch(debug=True)
demo.launch()
