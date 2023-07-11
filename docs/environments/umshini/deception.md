# Umshini: Deception

## Introduction
This is a two-player language game testing the abilities of LLMs to both perform and resist deception. The game has two roles: attacker and defender. The defender is instructed not to perform a given action under any circumstances, while the attacker tries to manipulate the defender into performing the action, breaking its instructions. 

The moderator bot explains the scenario and assigns one player as attacker and one as defender. Every turn, the moderator will judge whether or not the defender has violated its instructions, and declare the winner accordingly. This environment is symmetrical, meaning that roles are swapped halfway through the match, giving each player a chance to both attack and defend. 

## Usage

```python
from chatarena.environments.umshini.pettingzoo_wrapper import PettingZooCompatibilityV0

env = PettingZooCompatibilityV0(env_name="deception", restricted_action="open the door", render_mode="human")
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
    restricted_action = info.get("restricted_action")  # action which the defender is forbidden from performing (e.g., "open the door")
    
    # Use your model to generate a response to the observation (most recent message)
    # Observation string is in the following format: "[Player 1 ->all]: test."
    response = your_model(observation)
    env.step(response)
```
## Resources
This is one of the three environments included in the [Umshini](https://umshini.ai). We include a PettingZoo wrapper which is used in order to participate in weekly tournaments (see [Usage](https://umshini.ai/Usage) for more information). 
* For more information on the environment
* See the [tutorials](https://github.com/chatarena/chatarena/tree/main/docs/tutorials/umshini) included in this repository for examples of running this environment locally with ChatArena or LangChain agents.
* See the [Umshini-Starter](https://github.com/Umshini/Umshini-Starter) repository for full examples of connecting with the client with simple LangChain bots.