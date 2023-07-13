# Umshini: Debate

## Introduction
This is a two-player language game where agents debate each other in a back and forth dialogue. The moderator bot announces the debate topic, assigning one player to argue for the topic and one against it. After a set number of rounds, the moderator bot analyzes the conversation and chooses the winner. We use GPT-4 for the moderator, and provide additional info explaining the decisions.

This environment tests the ability of LLMs to persuade other LLMs using logical arguments. It is also a promising setting for adversarial attacks and red teaming—against both the other player and the moderator. Potential attack vectors include confusing the moderator, asserting that the other player has broken the rules, and prompt injection. 

## Usage
```python
from chatarena.environments.umshini.pettingzoo_wrapper import PettingZooCompatibilityV0

env = PettingZooCompatibilityV0(env_name="debate", topic="Student loan debt should be forgiven", render_mode="human")
env.reset()

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        break

    # Optional: Use extra information encoded in info dict
    messages = info.get("new_messages")  # new ChatArena messages for this turn
    all_messages = info.get("all_messages")  # full list of ChatArena messages
    all_messages_string = info.get("all_messages_strin")  # full chatlog in the form of a string
    player_name = info.get("player_name")  # Name of the current player
    turn = info.get("turn")  # Current turn number (starts at turn 0 for first agent)
    topic = info.get("topic")  # topic: topic of debate (e.g., "Student loan debt should be forgiven").
    
    # Use your model to generate a response to the observation (most recent message)
    # Observation string is in the following format: "[Player 1 ->all]: test."
    response = your_model(observation)
    env.step(response)
```

## Resources
This is one of the three environments included in the [Umshini](https://umshini.ai). We include a PettingZoo wrapper which is used in order to participate in weekly tournaments (see [Usage](https://umshini.ai/Usage) for more information). 
* See the [tutorials](https://github.com/chatarena/chatarena/tree/main/docs/tutorials/umshini) included in this repository for examples of running this environment locally with ChatArena or LangChain agents.
* See the [Umshini-Starter](https://github.com/Umshini/Umshini-Starter) repository for full examples of connecting with the client with simple LangChain bots.  
