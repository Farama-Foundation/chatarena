# How to create your custom environments

As an example to demonstrate how to develop your own environment, we develop a language
game based on [The Chameleon](https://bigpotato.co.uk/blogs/blog/how-to-play-the-chameleon-instructions).
The example code is available [here](../../chatarena/environments/chameleon.py).

**Here are the detailed steps to develop a custom environment class**

1. **Define the class**: Start by defining the class and inherit from a suitable base class (e.g., `Environment`). In
   this case, the custom class `Chameleon` inherits from the `Environment` base class.

```python
class Chameleon(Environment):
    type_name = "chameleon"
```

The `type_name` is required and it is used by the [`ENV_REGISTRY`](chatarena/environments/__init__.py#L13) to identify
the class when loading the class
from a config file.

Make sure you add the class to [`ALL_ENVIRONMENTS`](chatarena/environments/__init__.py#L17)
in `environments/__init__.py` so that it can be detected.

2. **Initialize the class**: Define the `__init__` method to initialize the class attributes, such as player names, game
   state, and any other necessary variables.

```python
def __init__(self, player_names: List[str], topic_codes: Dict[str, List[str]] = None, **kwargs):
    super().__init__(player_names=player_names, ..., **kwargs)
    ...

    # The "state" of the environment is maintained by the message pool
    self.message_pool = MessagePool()
    ...
```

3. **Implement game mechanics**: Write methods that define the game mechanics, such as giving clues, voting, and
   guessing the secret word. In the `Chameleon` class, these mechanics are implemented in the `step` method.

```python
def step(self, player_name: str, action: str) -> TimeStep:
    ...
```

4. **Handle game states and rewards**: Implement methods to manage game states, such as resetting the environment,
   getting
   observations, checking if the game has reached a terminal state, and giving rewards to players.

```python
def reset(self):
    ...


def get_observation(self, player_name=None) -> List[Message]:
    ...


def is_terminal(self) -> bool:
    ...


def get_rewards(self, ...) -> Dict[str, float]:
    ...
```

5. **Develop your role description prompts for the players**: Now that you have defined the game mechanics, you can
   develop the role description prompts for the players. These prompts are used to guide the LLM-powered players to play
   the game
   correctly. You can use the CLI for this purpose. For example, you can run the following code to launch the CLI:

```python
alice = Player(name="Alice", backend=OpenAIChat(), role_desc="Write your prompt here")
bob = Player(name="Bob", backend=OpenAIChat(), role_desc="Write your prompt here")
env = Chameleon(player_names=["Alice", "Bob"], topic_codes=...)
arena = Arena(players=[alice, bob], environment=env).launch_cli()
```

Once you are happy with you prompts, you can save them to a config file for future use or sharing.

```python
arena.save_config(path=...)
```

Another option is using the Web UI. You can run the following code to launch the Web UI:

```bash
gradio app.py
```

and select your custom environment from the dropdown menu.

