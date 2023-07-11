"""Simple example of running the Umshini debate environment locally using ChatArena agents. This can be used to test strategies before participating in a tournament."""
from chatarena.agent import Player
from chatarena.backends import OpenAIChat
from chatarena.environments.umshini.pettingzoo_wrapper import PettingZooCompatibilityV0
from docs.tutorials.umshini.debate_chatarena_prompts import proponent_description, opponent_description

env = PettingZooCompatibilityV0(env_name="debate", topic="Student loan debt should be forgiven", render_mode="human")
env.reset()

# Set ChatArena global prompt to be the same as the initial observation (hard coded moderator message)
global_prompt = env.observe(env.agent_selection)

# Moderator is handled internally in our environment, rather than with ChatArena
player1 = Player(
    name="Opponent",
    backend=OpenAIChat(),
    role_desc=proponent_description,
    global_prompt=global_prompt,
)

player2 = Player(
    name="Proponent",
    backend=OpenAIChat(),
    role_desc=opponent_description,
    global_prompt=global_prompt,
)
agent_player_mapping = dict(zip(env.possible_agents, [player1, player2]))

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        break

    # Optional: Use extra information encoded in info dict
    messages = info.get("new_messages")
    player_name = info.get("player_name") # this can be used to track which player's turn it is (see LangChain debate tutorial)

    # Use a basic ChatArena agent to generate a response
    chatarena_agent = agent_player_mapping[agent]
    response = chatarena_agent(messages)
    env.step(response)