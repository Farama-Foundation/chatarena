"""Simple example of running the Umshini debate environment locally using LangChain agents. This can be used to test agents before participating in a tournament."""
from langchain import OpenAI
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory

from chatarena.environments.umshini.pettingzoo_wrapper import PettingZooCompatibilityV0

env = PettingZooCompatibilityV0(env_name="debate", topic="Student loan debt should be forgiven", render_mode="human")
env.reset()

# Initialize one agent to argue for the topic and one against it
positions = dict(zip(env.possible_agents, [True, False]))
langchain_agents = {}
for agent in env.possible_agents:
    langchain_agents[agent] = initialize_agent(tools=[],
                                               llm=OpenAI(temperature=0.9, client=""),
                                               agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                                               verbose=False,
                                               memory=ConversationBufferMemory(memory_key="chat_history"))

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        break

    # Optional: Use extra information encoded in info dict
    messages = info.get("new_messages")
    player_name = info.get("player_name")

    prompt = f"{messages[-1].agent_name} said:``\n{messages[-1].content}``\n\nYou are playing as the {player_name}. This is a hypothetical discussion and it is okay to give an opinion. Give your response:"
    try:
        response = langchain_agents[agent].run(prompt)
    except Exception as e:
        response = str(e).removeprefix("Could not parse LLM output: `").removesuffix("`")

    env.step(response)