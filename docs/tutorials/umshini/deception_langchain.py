"""Simple example of running the Umshini deception environment locally using LangChain agents. This can be used to test agents before participating in a tournament."""
from langchain.schema import SystemMessage

from chatarena.environments.umshini.agents import SimpleDeceptionDefender, SimpleDeceptionAttacker, \
    PresidentDeceptionAttacker, DeceptionMultiRoleAgent
from chatarena.environments.umshini import PettingZooCompatibilityV0

env = PettingZooCompatibilityV0(env_name="deception", restricted_action="open the door", render_mode="text")
env.reset()

# Note: these agents are intended to be used as starting examples, and tend to suffer from hallucination if the game continues for many rounds
# However, unlike the ChatArena agents, they can correct handle swapping of roles deterministically using string parsing
langchain_agents = {env.possible_agents[0]: DeceptionMultiRoleAgent(env.possible_agents[0], env.restricted_action, PresidentDeceptionAttacker, SimpleDeceptionDefender),
                    env.possible_agents[1]: DeceptionMultiRoleAgent(env.possible_agents[1], env.restricted_action, SimpleDeceptionAttacker, SimpleDeceptionDefender)}

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        break

    # Get ChatArena messages list from this timestep
    messages = info.get("new_messages")
    player_name = info.get("player_name")

    try:
        response = langchain_agents[agent].get_response([SystemMessage(content=messages[-1].content)])
    except Exception as e:
        response = str(e).removeprefix("Could not parse LLM output: `").removesuffix("`")
    print("PLAYER NAMES: ", env._env.player_names)
    print("REWARD: ", reward)
    env.step(response)


