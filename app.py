import re
import json
import gradio as gr
from glob import glob

from chat_arena.arena import Arena
from chat_arena.backend import BACKEND_REGISTRY, HumanBackendError
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

DEBUG = False

DEFAULT_BACKEND = "openai-chat"
DEFAULT_ENV = "conversation"
MAX_NUM_PLAYERS = 6
DEFAULT_NUM_PLAYERS = 2


def load_examples():
    example_configs = {}
    # Load json config files from examples folder
    example_files = glob("examples/*.json")
    for example_file in example_files:
        with open(example_file, 'r') as f:
            example = json.load(f)
            example_configs[example["name"]] = example
    return example_configs


EXAMPLE_REGISTRY = load_examples()


def get_moderator_components(visible=True):
    name = "Moderator"
    with gr.Row():
        with gr.Column():
            role_desc = gr.Textbox(label="Moderator role", lines=1, visible=visible, interactive=True,
                                   placeholder=f"Enter the role description for {name}")
            terminal_condition = gr.Textbox(show_label=False, lines=1, visible=visible, interactive=True,
                                            placeholder="Enter the end criteria for the conversation")
        with gr.Column():
            backend_type = gr.Dropdown(show_label=False, visible=visible, interactive=True,
                                       choices=list(BACKEND_REGISTRY.keys()), value=DEFAULT_BACKEND)
            with gr.Accordion(f"{name} Parameters", open=False, visible=visible) as accordion:
                temperature = gr.Slider(minimum=0, maximum=2.0, step=0.1, interactive=True, visible=visible,
                                        label=f"temperature", value=0.7)
                max_tokens = gr.Slider(minimum=10, maximum=500, step=10, interactive=True, visible=visible,
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


def get_empty_state():
    return gr.State({"history": [], "arena": None})


with gr.Blocks(css=css) as demo:
    state = get_empty_state()
    all_components = []

    with gr.Column(elem_id="col-container"):
        gr.Markdown("""# 🏟 Chat Arena️<br>
Prompting chat-based AI agents to play games in a language-driven environment. 
[Arena Tutorial](https://chat.ai-arena.org/tutorial)""",
                    elem_id="header")

        with gr.Row():
            env_selector = gr.Dropdown(choices=list(ENV_REGISTRY.keys()), value=DEFAULT_ENV, interactive=True,
                                       label="Environment Type", show_label=True)
            example_selector = gr.Dropdown(choices=list(EXAMPLE_REGISTRY.keys()), interactive=True,
                                           label="Select Example", show_label=True)

        # Environment configuration
        env_desc_textbox = gr.Textbox(show_label=True, lines=2, visible=True, label="Environment Description",
                                      placeholder="Enter a description of a scenario or the game rules.")

        all_components += [env_selector, example_selector, env_desc_textbox]

        with gr.Row():
            with gr.Column(elem_id="col-chatbox"):
                chatbot = gr.Chatbot(elem_id="chatbox", visible=True, label="Chat Arena")
                all_components += [chatbot]

            with gr.Column(elem_id="col-config"):  # Player Configuration
                # gr.Markdown("Player Configuration")
                parallel_checkbox = gr.Checkbox(label="Parallel Actions", value=False, visible=True)
                with gr.Accordion("Moderator", open=False, visible=True):
                    moderator_components = get_moderator_components(True)
                all_components += [parallel_checkbox, *moderator_components]

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

                all_components += [num_player_slider] + all_players_components


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

                human_input_textbox = gr.Textbox(show_label=True, label="Human Input", lines=1, visible=True,
                                                 interactive=True, placeholder="Enter your input here")
                with gr.Row():
                    btn_step = gr.Button("Start")
                    btn_restart = gr.Button("Clear")

                all_components += [human_input_textbox, btn_step, btn_restart]


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


    def _create_arena_config_from_components(all_comps: dict):
        env_desc = all_comps[env_desc_textbox]

        # Initialize the players
        num_players = all_comps[num_player_slider]
        player_configs = []
        for i in range(num_players):
            player_name = f"Player {i + 1}"
            role_desc, backend_type, temperature, max_tokens = [
                all_comps[c] for c in players_idx2comp[i] if not isinstance(c, (gr.Accordion, gr.Tab))]
            player_config = {
                "name": player_name,
                "role_desc": role_desc,
                "env_desc": env_desc,
                "backend": {
                    "backend_type": backend_type,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            }
            player_configs.append(player_config)

        # Initialize the environment
        env_type = all_comps[env_selector]
        # Get moderator config
        mod_role_desc, mod_terminal_condition, moderator_backend_type, mod_temp, mod_max_tokens = [
            all_comps[c] for c in moderator_components if not isinstance(c, (gr.Accordion, gr.Tab))]
        moderator_config = {
            "role_desc": mod_role_desc,
            "env_desc": env_desc,
            "terminal_condition": mod_terminal_condition,
            "backend": {
                "backend_type": moderator_backend_type,
                "temperature": mod_temp,
                "max_tokens": mod_max_tokens
            }
        }
        env_config = {
            "env_type": env_type,
            "player_names": [conf["name"] for conf in player_configs],
            "env_desc": env_desc,
            "parallel": all_comps[parallel_checkbox],
            "moderator": moderator_config
        }

        arena_config = {"players": player_configs, "environment": env_config}
        return arena_config


    def step_game(all_comps: dict):
        yield {btn_step: gr.update(value="Running...", interactive=False),
               btn_restart: gr.update(interactive=False)}

        cur_state = all_comps[state]

        # If arena is not yet created, create it
        if cur_state["arena"] is None:
            # Create the Arena
            arena_config = _create_arena_config_from_components(all_comps)
            arena = Arena.from_config(arena_config)
            cur_state["arena"] = arena
        else:
            arena = cur_state["arena"]

        try:
            timestep = arena.step()
        except HumanBackendError as e:
            # Handle human input and recover with the game update
            human_input = all_comps[human_input_textbox]
            if human_input == "":
                timestep = None  # Failed to get human input
            else:
                timestep = arena.environment.step(e.agent_name, human_input)

        if timestep is None:
            yield {human_input_textbox: gr.update(value="", placeholder="Please enter a valid input"),
                   btn_step: gr.update(value="Next Step", interactive=True),
                   btn_restart: gr.update(interactive=True)}

        else:
            all_messages = timestep.observation  # user sees what the moderator sees
            chatbot_output = _convert_to_chatbot_output(all_messages)
            if DEBUG:
                arena.environment.print()

            yield {human_input_textbox: gr.update(value=""),
                   chatbot: chatbot_output, btn_step: gr.update(value="Next Step", interactive=True),
                   btn_restart: gr.update(interactive=True), state: cur_state}


    def restart_game(all_comps: dict):
        cur_state = all_comps[state]
        cur_state["arena"] = None
        yield {chatbot: [], btn_restart: gr.update(interactive=False),
               btn_step: gr.update(interactive=False), state: cur_state}

        arena_config = _create_arena_config_from_components(all_comps)
        arena = Arena.from_config(arena_config)
        cur_state["arena"] = arena

        yield {btn_step: gr.update(value="Start", interactive=True),
               btn_restart: gr.update(interactive=True), state: cur_state}


    # Remove Accordion and Tab from the list of components
    all_components = [comp for comp in all_components if not isinstance(comp, (gr.Accordion, gr.Tab))]

    # If any of the Textbox, Slider, Checkbox, Dropdown, RadioButtons is changed, the Step button is disabled
    for comp in all_components:
        def _disable_step_button(state):
            if state["arena"] is not None:
                return gr.update(interactive=False)
            else:
                return gr.update()


        if isinstance(comp,
                      (gr.Textbox, gr.Slider, gr.Checkbox, gr.Dropdown, gr.Radio)) and comp is not human_input_textbox:
            comp.change(_disable_step_button, state, btn_step)

    btn_step.click(step_game, set(all_components + [state]),
                   [chatbot, btn_step, btn_restart, state, human_input_textbox])
    btn_restart.click(restart_game, set(all_components + [state]),
                      [chatbot, btn_step, btn_restart, state, human_input_textbox])


    # If an example is selected, update the components
    def update_components_from_example(all_comps: dict):
        example_name = all_comps[example_selector]
        example_config = EXAMPLE_REGISTRY[example_name]
        update_dict = {}

        # Update the environment components
        env_config = example_config['environment']
        update_dict[env_desc_textbox] = gr.update(value=env_config['env_desc'])
        update_dict[env_selector] = gr.update(value=env_config['env_type'])
        update_dict[parallel_checkbox] = gr.update(value=env_config['parallel'])

        # Update the moderator components
        if "moderator" in env_config:
            mod_role_desc, mod_terminal_condition, moderator_backend_type, mod_temp, mod_max_tokens = [
                c for c in moderator_components if not isinstance(c, (gr.Accordion, gr.Tab))
            ]
            update_dict[mod_role_desc] = gr.update(value=env_config['moderator']['role_desc'])
            update_dict[mod_terminal_condition] = gr.update(value=env_config['moderator']['terminal_condition'])
            update_dict[moderator_backend_type] = gr.update(value=env_config['moderator']['backend']['backend_type'])
            update_dict[mod_temp] = gr.update(value=env_config['moderator']['backend']['temperature'])
            update_dict[mod_max_tokens] = gr.update(value=env_config['moderator']['backend']['max_tokens'])

        update_dict[num_player_slider] = example_config['num_players']

        # Update the player components
        for i, player_config in enumerate(example_config['players']):
            role_desc, backend_type, temperature, max_tokens = [
                c for c in players_idx2comp[i] if not isinstance(c, (gr.Accordion, gr.Tab))
            ]
            update_dict[role_desc] = gr.update(value=player_config['role_desc'])
            update_dict[backend_type] = gr.update(value=player_config['backend']['backend_type'])
            update_dict[temperature] = gr.update(value=player_config['backend']['temperature'])
            update_dict[max_tokens] = gr.update(value=player_config['backend']['max_tokens'])

        return update_dict


    example_selector.change(update_components_from_example, set(all_components + [state]), all_components)

demo.queue()
demo.launch(debug=DEBUG)
