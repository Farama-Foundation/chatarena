"""Build a role-play game between two chatbots using OpenAI's GPT-3 API."""
import gradio as gr
import os
import openai
from time import sleep
import re

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


def play_game(*args):
    num_players, system_desc, next_speaker_strategy, auto_terminate, max_turns = args[:5]

    offset = 5
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
                chatbot_output.append((new_msg, None))
            else:
                chatbot_output.append((None, new_msg))
        return chatbot_output

    # Main loop: Play the game
    for turn in range(max_turns):
        try:
            arena.step()
            all_messages = arena.get_visible_history(moderator)  # user sees what the moderator sees
            chatbot_output = _convert_to_chatbot_output(all_messages)
            yield chatbot_output, get_empty_state()  # Update the chatbot UI output
            sleep(1.0)

            if arena.is_terminal():
                break
        except Exception as e:
            print(e)


def clear_conversation():
    return [gr.update(value=None, visible=True) for _ in range(1 + num_players)] + [None, get_empty_state()]


css = """
      #col-container {max-width: 80%; margin-left: auto; margin-right: auto; flex-flow: column;}
      #header {text-align: center;}
      #chatbox {min-height: 400px; flex: 0 1 auto;}
      #label {font-size: 0.8em; padding: 0.5em; margin: 0;}
      .message { font-size: 1.2em; }
      """

# prompt_template_preview {padding: 1em; border-width: 1px; border-style: solid; border-color: #e0e0e0; border-radius: 4px;}
# total_tokens_str {text-align: right; font-size: 0.8em; color: #666; height: 1em;}
# chatbox {flex: 0 1 auto;}
# chatbox {min-height: 400px;}

with gr.Blocks(css=css) as demo:
    state = gr.State(get_empty_state())

    # with gr.Column(elem_id="col-container"):
    gr.Markdown("""# Chat Arena 🏟️ <br>
    Prompt two chat-based AI agents to play a role-play game.""",
                elem_id="header")

    all_components = []  # keep track of all components so we can use them later

    # gr.Markdown("Configurations")
    num_players_component = gr.Slider(minimum=2, maximum=6, value=2, step=1, interactive=True,
                                      label="Number of Players")
    num_players = num_players_component.value  # TODO: make this dynamic and update the UI when it change
    gr.Markdown("Scenario/Rule Description")
    system_desc = gr.Textbox(show_label=False, lines=3,
                             label="System Description",
                             placeholder="Enter a description of a scenario or the game rules.",
                             visible=True)

    with gr.Row():
        next_speaker_strategy = gr.Radio(label="Next Speaker Strategy",
                                         choices=NextSpeakerStrategy.options(),
                                         value=NextSpeakerStrategy.ROTARY.value, visible=True)
        with gr.Column():
            auto_terminate = gr.Checkbox(label="Auto-terminate Conversation", value=False, visible=True)
            max_turns = gr.Slider(minimum=4, maximum=32, value=8, step=1, interactive=True,
                                  label="Max turns per game")

    # All game-level metadata
    all_components += [num_players_component, system_desc, next_speaker_strategy, auto_terminate, max_turns]

    with gr.Accordion("Moderator Configuration", open=False):
        moderator_components = Moderator.get_components()
        all_components.extend(moderator_components)

    with gr.Row():
        for player_id in range(1, num_players + 1):
            with gr.Column():
                gr.Markdown(f"Player {player_id}")
                player_components = Player.get_components("Player " + str(player_id))
                all_components.extend(player_components)

    with gr.Row():
        btn_play = gr.Button("Play")
        btn_clear_conversation = gr.Button("Restart")

    chatbot = gr.Chatbot(elem_id="chatbox")

    btn_play.click(play_game,
                   all_components,
                   [chatbot, state])
    # btn_clear_conversation.click(clear_conversation, [], all_components)

# define queue - required for generators
demo.queue()
# demo.launch(debug=True, height='800px')
# demo.launch()
demo.launch(debug=True)
