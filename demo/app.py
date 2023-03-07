"""Build a role-play game between two chatbots using OpenAI's GPT-3 API."""
import gradio as gr
import os
import openai
from time import sleep
import re

from chat_arena.agent import Agent, Player, Moderator

openai.api_key = os.environ.get("OPENAI_API_KEY")

prompt_templates = {"Default ChatGPT": ""}


def get_empty_state():
    return {"total_tokens": 0, "messages": []}


def substitute_new_lines(text):
    # substitute multiple new lines to a single HTML <br> tag
    return re.sub(r'\n+', '<br>', text.strip())


def chatbot_tuple(msg, id):
    msg_tuple = [None for _ in range(num_players)]
    msg_tuple[num_players - id] = msg
    return tuple(msg_tuple)


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
    offset = 4
    assert len(args) == 3 * num_players + offset + 2
    scenario_desc = args[0]
    moderator_role = args[1]
    rotary_speaker = args[2]
    auto_terminate = args[3]
    player_roles = args[offset: num_players + offset]
    player_temperatures = args[num_players + offset: 2 * num_players + offset]
    player_max_tokens = args[2 * num_players + offset: 3 * num_players + offset]
    max_turns = args[3 * num_players + offset]
    state = args[3 * num_players + offset + 1]

    # Initialize moderator
    moderator = Moderator(moderator_role, scenario_desc, 0.5, 30, num_players, max_turns)

    # Initialize players
    all_players = []
    for player_id, role, temperature, max_tokens in zip(range(1, num_players + 1), player_roles, player_temperatures,
                                                        player_max_tokens):
        player = Player(player_id, role, scenario_desc, temperature, max_tokens)
        all_players.append(player)

    all_messages, chatbot_output = [], []

    for turn in range(max_turns):
        try:
            next_speaker_idx = moderator.get_next_speaker(rotary_speaker=rotary_speaker)
            next_speaker = all_players[next_speaker_idx]

            msg = next_speaker.get_response()
            # Broadcast message to other players
            for other_player in all_players:
                if other_player != next_speaker:
                    other_player.add_message(msg)
            # Moderator also gets to see the message
            moderator.add_message(f"[{next_speaker.name}]: {msg}")

            # Add message to chatbot output history
            all_messages.append({"role": next_speaker.name, "content": msg, "type": "message"})
            chatbot_output.append(chatbot_tuple(substitute_new_lines(msg), next_speaker.player_id))
            yield chatbot_output, get_empty_state()

            if auto_terminate and moderator.is_conversation_over():
                break

        except Exception as e:
            print(e)

    print(all_messages)


num_players = 2


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

    gr.Markdown("### Scenario/Rule Description")
    scenario_desc = gr.Textbox(show_label=False, lines=3,
                               placeholder="Enter a description of the scenario or game rules.",
                               visible=True)

    with gr.Accordion("Moderator Configuration", open=False):
        moderator_role = gr.Textbox(show_label=False, lines=2, visible=True,
                                    placeholder=f"Enter the role description for the Moderator",
                                    value=Moderator.get_default_role(num_players))
        rotary_speaker = gr.Checkbox(label="Rotary Speaker", value=True, visible=True)
        auto_terminate = gr.Checkbox(label="Auto-terminate Conversation", value=False, visible=True)

    with gr.Row():
        player_roles = []
        for player_id in range(1, num_players + 1):
            with gr.Column():
                gr.Markdown(f"### Player {player_id}")
                role = gr.Textbox(show_label=False, lines=3, visible=True,
                                  placeholder=f"Enter the role description for Player {player_id}")
                player_roles.append(role)

    player_temperatures, player_max_tokens = [], []
    with gr.Accordion("Advanced Parameters", open=False):
        with gr.Row():
            for player_id in range(1, num_players + 1):
                with gr.Column():
                    temperature = gr.Slider(minimum=0, maximum=2.0, value=0.7, step=0.1, interactive=True,
                                            label=f"Player {player_id} temperature (higher = more creative/chaotic)")
                    max_tokens = gr.Slider(minimum=100, maximum=1000, value=300, step=10, interactive=True,
                                           label=f"Player {player_id} max tokens per response")
                    player_temperatures.append(temperature)
                    player_max_tokens.append(max_tokens)

        max_turns = gr.Slider(minimum=1, maximum=12, value=8, step=1, interactive=True,
                              label="Max turns per game")

    with gr.Row():
        btn_play = gr.Button("Play")
        btn_clear_conversation = gr.Button("Restart")

    chatbot = gr.Chatbot(elem_id="chatbox")

    btn_play.click(play_game,
                   [scenario_desc, moderator_role, rotary_speaker, auto_terminate, *player_roles, *player_temperatures,
                    *player_max_tokens, max_turns, state],
                   [chatbot, state])
    btn_clear_conversation.click(clear_conversation, [], [scenario_desc, *player_roles, chatbot, state])

# define queue - required for generators
demo.queue()
# demo.launch(debug=True, height='800px')
# demo.launch()
demo.launch(debug=True)
