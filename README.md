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

## Usage

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

## Documentation

For more detailed information on the available functions and classes, please refer to
the [documentation](link-to-documentation).

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
the maintainer at [chat-arena@gmail.com](mailto:chat-arena@gmail.com).

Happy chatting!


