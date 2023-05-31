# How to use PettingZoo compatibility wrapper

This tutorial provides a simple example to demonstrate how to use a ChatArena environment with [PettingZoo](https://github.com/Farama-Foundation/PettingZoo).

1. **Load the environment**
```python
from chatarena.arena import Arena

arena = Arena.from_config("examples/pettingzoo_env_example.json")
```

2. **Wrap the environment**
```python
from chatarena.pettingzoo_compatibility import PettingZooCompatibilityV0
env = PettingZooCompatibilityV0(env=arena, render_mode="human", max_turns=5)
env.reset()

print("OBS SPACE: ", env.observation_space(env.agent_selection))
print("ACT SPACE: ", env.action_space(env.agent_selection))
```

3. **Run the environment**
```python
agent_player_mapping = {agent: player_obj
                        for agent in env.possible_agents
                        for player_obj in env._env.players}

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    # Use chat arena agent to generate response (TODO: use manual input backend rather than this method of input)
    chatarena_agent = agent_player_mapping[agent]
    messages = env._env.environment.message_pool.get_visible_messages(agent, turn=env.current_turn)
    response = chatarena_agent(messages)

    env.step(response)
    print("---")
env.close()
```