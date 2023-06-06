from chatarena.agent import Player
from chatarena.backends import OpenAIChat
from chatarena.environments.umshini.pettingzoo_wrapper import PettingZooCompatibilityV0
from docs.tutorials.umshini.debate_chatarena_prompts import proponent_description, opponent_description

topic = "Student loan debt should be forgiven"
env = PettingZooCompatibilityV0(env_name="debate", topic=topic, render_mode="text")
initial_obs, info = env.reset()


# Set ChatArena global prompt to be the same as the initial observation (hard coded moderator message)
global_prompt = initial_obs

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

    # get ChatArena messages list from this timestep
    messages = info.get("new_messages")

    # Use a basic ChatArena agent to generate a response
    chatarena_agent = agent_player_mapping[agent]
    response = chatarena_agent(messages)
    env.step(response)