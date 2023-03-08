"""Build a role-play game between two chatbots using OpenAI's GPT-3 API."""
import gradio as gr
import os
import openai
from time import sleep
import re

from chat_arena.agent import Player, Moderator

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
    # return None, get_empty_state()
    # assert len(args) == 3 * num_players + offset + 2
    num_players, system_desc, rotary_speaker, auto_terminate, max_turns = args[:5]

    offset = 5
    moderator, offset = Moderator.parse_components(args, "Moderator", start_idx=offset)

    all_players = []
    for player_id in range(1, num_players + 1):
        player, offset = Player.parse_components(args, f"Player {player_id}", start_idx=offset)
        all_players.append(player)

    all_messages, chatbot_output = [], []

    def log_message(msg, role, type, index=0, include_role_in_ui=False):
        all_messages.append({"role": role, "content": msg, "type": type})

        # Preprocess message for chatbot output
        msg = re.sub(r'\n+', '<br>', msg.strip())

        if include_role_in_ui:
            msg = f"[{role}]: {msg}"

        # Determine which side to display the message, 0 for left-sided bubble, 1 for right-sided bubble
        if index == 0:
            chatbot_tuple = (None, msg)
        elif index == 1:
            chatbot_tuple = (msg, None)
        else:
            raise ValueError("Index must be 0 or 1")

        chatbot_output.append(chatbot_tuple)

    for turn in range(max_turns):
        try:
            if rotary_speaker:  # Get the next speaker in a round-robin fashion
                next_player_idx = turn % num_players
            else:  # Get the next speaker by asking the moderator
                next_player_idx = moderator.get_next_player()

            next_player = all_players[next_player_idx]
            player_msg = next_player.get_response()
            log_message(player_msg, next_player.name, "player_msg", index=0, include_role_in_ui=True)
            yield chatbot_output, get_empty_state()  # Update the chatbot UI output

            # Broadcast message to other players
            for other_player in all_players:
                if other_player != next_player:
                    other_player.add_message(player_msg)
            # Moderator also gets to see the message
            # moderator.add_message(f"[{next_player.name}]: {player_msg}")
            moderator.add_message(player_msg)

            # moderator_msg = moderator.get_response(temperature=0.0, max_tokens=30)
            # log_message(moderator_msg, moderator.name, "moderator_msg", index=0, include_role_in_ui=True)
            # yield chatbot_output, get_empty_state()  # Update the chatbot UI output

            sleep(1.0)

            if auto_terminate and moderator.is_game_end():
                break

        except Exception as e:
            print(e)

    print(all_messages)


# num_players = 2


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

    gr.Markdown("## Game Configuration")
    num_players_component = gr.Slider(minimum=2, maximum=4, value=2, step=1, interactive=True,
                                      label="Number of Players")
    num_players = num_players_component.value  # TODO: make this dynamic and update the UI when it change
    # gr.Markdown("### Scenario/Rule Description")
    system_desc = gr.Textbox(show_label=False, lines=3,
                             label="System Description",
                             placeholder="Enter a description of a scenario or the game rules.",
                             visible=True)
    rotary_speaker = gr.Checkbox(label="Rotary Speaker", value=True, visible=True)
    auto_terminate = gr.Checkbox(label="Auto-terminate Conversation", value=True, visible=True)
    max_turns = gr.Slider(minimum=4, maximum=32, value=8, step=1, interactive=True,
                          label="Max turns per game")
    # All game-level metadata
    all_components += [num_players_component, system_desc, rotary_speaker, auto_terminate, max_turns]

    with gr.Accordion("Moderator Configuration", open=False):
        moderator_components = Moderator.get_components()
        all_components.extend(moderator_components)

    with gr.Row():
        for player_id in range(1, num_players + 1):
            with gr.Column():
                gr.Markdown(f"### Player {player_id}")
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
