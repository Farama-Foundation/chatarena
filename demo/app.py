"""Build a role-play game between two chatbots using OpenAI's GPT-3 API."""
import gradio as gr
import os
import openai
from time import sleep
import re
from functools import partial

from chat_arena.agent import Player, Moderator
from chat_arena.arena import Arena, NextSpeakerStrategy

openai.api_key = os.environ.get("OPENAI_API_KEY")


def get_empty_state():
    return {"total_tokens": 0, "messages": []}


# def download_prompt_templates():
#     url = "https://raw.githubusercontent.com/f/awesome-chatgpt-prompts/main/prompts.csv"
#     response = requests.get(url)
#
#     for line in response.text.splitlines()[1:]:
#         act, prompt = line.split('","')
#         prompt_templates[act.replace('"', '')] = prompt.replace('"', '')
#
#     choices = list(prompt_templates.keys())
#     return gr.update(value=choices[0], choices=choices)


def play_game(*args, num_players=2):
    # Clear the chatbot UI output and hide the other components
    yield gr.update(value=[], visible=True), gr.update(value="Running...", interactive=False), get_empty_state()

    system_desc, next_speaker_strategy, auto_terminate, max_turns = args[:4]

    offset = 4
    moderator, offset = Moderator.parse_components(args, "Moderator", start_idx=offset)

    all_players = []
    for player_id in range(1, num_players + 1):
        player, offset = Player.parse_components(args, f"Player {player_id}", start_idx=offset)
        all_players.append(player)

    # Create the arena to manage the game environment
    arena = Arena(all_players, moderator, next_speaker_strategy=next_speaker_strategy,
                  max_turns=max_turns, auto_terminate=auto_terminate)

    def _convert_to_chatbot_output(all_messages):
        chatbot_output = []
        for i, message in enumerate(all_messages):
            role, msg = message.role, message.content
            new_msg = re.sub(r'\n+', '<br>', msg.strip())  # Preprocess message for chatbot output
            new_msg = f"[{role.name}]: {new_msg}"  # Add role to the message

            if role == moderator:
                # chatbot_output.append((new_msg, None))
                pass  # Disable moderator output for now
            else:
                chatbot_output.append((None, new_msg))
        return chatbot_output

    # Main loop: Play the game
    for turn in range(max_turns):
        try:
            arena.step()
            all_messages = arena.get_visible_history(moderator)  # user sees what the moderator sees
            chatbot_output = _convert_to_chatbot_output(all_messages)
            # Update the chatbot UI output
            yield chatbot_output, gr.update(), get_empty_state()
            sleep(1.0)

            if arena.is_terminal():
                break
        except Exception as e:
            print(e)

    yield gr.update(), gr.update(value="Run", interactive=True), get_empty_state()


css = """
      #col-container {max-width: 80%; margin-left: auto; margin-right: auto; flex-flow: column;}
      #header {text-align: center;}
      #chatbox {min-height: 400px; flex: 0 1 auto;}
      #label {font-size: 2em; padding: 0.5em; margin: 0;}
      .message {font-size: 1.2em;}
      """

# auto-term-col {max-width: 33%;}
# prompt_template_preview {padding: 1em; border-width: 1px; border-style: solid; border-color: #e0e0e0; border-radius: 4px;}
# total_tokens_str {text-align: right; font-size: 0.8em; color: #666; height: 1em;}
# chatbox {flex: 0 1 auto;}
# chatbox {min-height: 400px;}

with gr.Blocks(css=css) as demo:
    state = gr.State(get_empty_state())

    with gr.Column(elem_id="col-container"):
        gr.Markdown("""# 🏟 Chat Arena️<br>
        Prompting chat-based AI agents to play games in a language-driven environment.""",
                    elem_id="header")

        all_components = []  # keep track of all components so we can use them later

        with gr.Accordion("Configuration", open=True) as config_accordion:
            # num_players_component = gr.Slider(minimum=2, maximum=2, value=2, step=1, interactive=False,
            #                                   label="Number of Players", visible=False)

            gr.Markdown("Scenario/Rule Description")
            system_desc = gr.Textbox(show_label=False, lines=3,
                                     label="System Description",
                                     placeholder="Enter a description of a scenario or the game rules.",
                                     visible=True)

            with gr.Row():
                next_speaker_strategy = gr.Radio(label="Next Speaker Strategy",
                                                 choices=NextSpeakerStrategy.options(),
                                                 value=NextSpeakerStrategy.ROTARY.value, visible=True)
                with gr.Column(elem_id="auto-term-col"):
                    auto_terminate = gr.Checkbox(label="Auto-terminate Conversation", value=False, visible=True)
                    max_turns = gr.Slider(minimum=4, maximum=32, value=8, step=1, interactive=True,
                                          label="Max turns per game")

            # All game-level metadata
            all_components += [system_desc, next_speaker_strategy, auto_terminate, max_turns]

            with gr.Accordion("Moderator Configuration", open=False):
                moderator_components = Moderator.get_components()
                all_components.extend(moderator_components)

            with gr.Tab("Two Players"):
                all_player_components_2 = []
                with gr.Row():
                    for player_id in range(1, 3):
                        with gr.Column():
                            gr.Markdown(f"Player {player_id}")
                            player_components = Player.get_components("Player " + str(player_id))
                            all_player_components_2.extend(player_components)

                with gr.Row():
                    btn_play_2 = gr.Button("Play")

            with gr.Tab("Three Players"):
                all_player_components_3 = []
                with gr.Row():
                    for player_id in range(1, 4):
                        with gr.Column():
                            gr.Markdown(f"Player {player_id}")
                            player_components = Player.get_components("Player " + str(player_id))
                            all_player_components_3.extend(player_components)

                with gr.Row():
                    btn_play_3 = gr.Button("Play")

            with gr.Tab("Four Players"):
                all_player_components_4 = []
                with gr.Row():
                    for player_id in [1, 2]:
                        with gr.Column():
                            gr.Markdown(f"Player {player_id}")
                            player_components = Player.get_components("Player " + str(player_id))
                            all_player_components_4.extend(player_components)

                with gr.Row():
                    for player_id in [3, 4]:
                        with gr.Column():
                            gr.Markdown(f"Player {player_id}")
                            player_components = Player.get_components("Player " + str(player_id))
                            all_player_components_4.extend(player_components)

                with gr.Row():
                    btn_play_4 = gr.Button("Play")

        chatbot = gr.Chatbot(elem_id="chatbox", visible=False, label="Chat Arena")

    btn_play_2.click(partial(play_game, num_players=2), all_components + all_player_components_2,
                     [chatbot, btn_play_2, state], api_name="two_players_arena")
    btn_play_3.click(partial(play_game, num_players=3), all_components + all_player_components_3,
                     [chatbot, btn_play_3, state], api_name="three_players_arena")
    btn_play_4.click(partial(play_game, num_players=4), all_components + all_player_components_4,
                     [chatbot, btn_play_4, state], api_name="four_players_arena")

# define queue - required for generators
demo.queue()
# demo.launch(debug=True, height='800px')
# demo.launch()
demo.launch(debug=True)
