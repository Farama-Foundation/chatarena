<h1 align="center"> 🏟 <span style="color:orange">Chat Arena</span> </h1>
<h3 align="center">
    <p>Multi-Agent Language Game Environments for LLMs</p>
</h3>

---

Chat Arena is a Python library designed to facilitate communication, collaboration and competition between multiple LLMs
in a language-driven environment. It provides the following features:

- Language-driven Game Environment: it provides a framework for creating a language-driven environment.
- Infrastructure for Multi-LLM Interaction: it enables rapid definition and creation of LLM-based agents, and seamlessly
  communication, collaboration, and competition between them.
- Playground & Testbed for C3 Capabilities: it provides a set of environments for evaluating and developing the
  **communication, collaboration, and competition**  (C3) capabilities of LLMs.

## Getting Started

### Installation

Requirements:

- Python >= 3. 7
- OpenAI API key (optional, for using GPT-3.5-turbo or GPT-4 as an LLM agent)

Install with pip:

```bash
pip install chatarena
```

or install from this repository:

```bash
git clone https://github.com/chatarena/chatarena
cd chatarena
pip install -e .
```

To use GPT-3 as an LLM agent, set your OpenAI API key:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

### Launch the Demo

To launch the demo, run the following command in the root directory of the repository:

```shell
gradio app.py
```

This will launch a demo UI of the Chat Arena in your browser.

## Basic Usage

### Key Concepts

- **Player**: a player is an agent that can interact with other players in a game environment. A player can be a human
  or
  a large language model (LLM). A player is defined by its name, its backend, and its role.
    - **Backend**: a backend is a Python class that defines how a player interacts with other players. A backend can be
      a
      human, a LLM, or a combination of them. A backend is defined by its name, its type, and its parameters.
- **Environment**: an environment is a Python class that defines the rules of a game. An environment is defined by its
  name, its type, and its parameters.
    - **Moderator**: a moderator is a Python class that defines how the game is played. A moderator is defined by its
      name,
      its type, and its parameters.
- **Arena**: an arena is a Python class that defines the overall game. An arena is defined by its name, its type, and
  its
  parameters.

### Step 1: Defining Multiple Players with LLM Backend

```python
from chatarena.agent import Player
from chatarena.backends import OpenAIChat

# Describe the environment (which is shared by all players)
environment_description = "It is in a university classroom ..."

# A "Professor" player
player1 = Player(name="Professor", backend=OpenAIChat(),
                 role_desc="You are a professor in ...",
                 global_prompt=environment_description)
# A "Student" player
player2 = Player(name="Student", backend=OpenAIChat(),
                 role_desc="You are a student who is interested in ...",
                 global_prompt=environment_description)
# A "Teaching Assistant" player
player3 = Player(name="Teaching assistant", backend=OpenAIChat(),
                 role_desc="You are a teaching assistant of module ...",
                 global_prompt=environment_description)
```

### Step 2: Create a Language Game Environment

You can also create a language model-driven environment and add it to the Chat Arena:

```python
from chatarena.environments.conversation import Conversation

env = Conversation(player_names=[p.name for p in [player1, player2, player3]])
```

### Step 3: Run the Language Games using Arena

Arena is a utility class to help you run language games.

```python
from chatarena.arena import Arena

arena = Arena(players=[player1, player2, player3],
              environment=env, global_prompt=environment_description)
# Run the game for 10 steps
arena.run(num_steps=10)

# Alternatively, you can run your own main loop
for _ in range(10):
    arena.step()
    # Your code goes here ...
```

You can easily save your game play history to file

```python
arena.save_history(path=...)
```

and save your game config to file

```python
arena.save_config(path=...)
```

### Other Utilities

Load Arena from config file (here we use `examples/nlp-classroom-3players.json` in this repository as an example)

```python
arena = Arena.from_config("examples/nlp-classroom-3players.json")
arena.run(num_steps=10)
```

Run the game in an interactive CLI interface

```python
arena.launch_cli()
```

## Advanced Usage

### `ModeratedConversation`

We support a more advanced environment called `ModeratedConversation` that allows you to **control the game dynamics
using an LLM**.
The moderator is a special player that controls the game state transition and determines when the game ends.
For example, you can define a moderator that track the board status of a board game, and end the game when a player
wins.
You can try out our Tic-tac-toe and Rock-paper-scissors games to get a sense of how it works:

```python
# Tic-tac-toe game
Arena.from_config("examples/tic-tac-toe.json").launch_cli()

# Rock-paper-scissors game
Arena.from_config("examples/rock-paper-scissors.json").launch_cli()
```

### Defining your Custom Environment

You can define your own environment by extending the `Environment` class.
We provide [an example](chatarena/environments/chameleon.py) to demonstrate how to define a custom environment.
In this example, we develop a language
game based on [The Chameleon](https://bigpotato.co.uk/blogs/blog/how-to-play-the-chameleon-instructions).

**Steps to Develop a Custom Class**

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
    super().__init__(player_names=player_names, **kwargs)

    if topic_codes is None:
        topic_codes = DEFAULT_TOPIC_CODES
    self.topic_codes = topic_codes

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

You may create helper methods to perform common operations for game mechanics such as

```python
def _text2vote(self, text) -> str:
    ...


def _is_true_code(self, text) -> bool:
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

9. For example, in the `Chameleon` class, the role description prompts are defined in the `role_descs`
   attribute.

Test your custom class by simulating a game or by integrating it into an existing
framework, such as an OpenAI Gym environment. Ensure that the class works as expected and correctly implements the
desired game mechanics.

[//]: # (## Documentation)

[//]: # (For more detailed information on the available functions and classes, please refer to)

[//]: # (the [documentation]&#40;link-to-documentation&#41;.)

## Contributing

We welcome contributions to improve and extend Chat Arena. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes to the new branch.
4. Create a pull request describing your changes.
5. We will review your pull request and provide feedback or merge your changes.

Please ensure your code follows the existing style and structure.

## License

Chat Arena is released under the [Apache License](LICENSE).

## Contact

If you have any questions or suggestions, feel free to open an issue or submit a pull request. You can also reach out to
the maintainer at [chatarena.dev@gmail.com](mailto:chatarena.dev@gmail.com).

Happy chatting!


