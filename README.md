<font size="+2" > 
<h1 align="center"> 🏟 <span style="color:coral">Chat Arena</span> </h1>
</font>
<h3 align="center">
    <p>Multi-Player/Agent Language Game Environments/Platform/Library</p>
</h3>

---

Chat Arena is a Python library designed to facilitate communication, collaboration and competition between multiple LLMs
in a language-driven environment. It provides the following features:

- Language-driven Game Environment: it provides a framework for creating a language-driven environment.
- Infrastructure for Multi-LLM Interaction: it enables rapid definition and creation of LLM-based agents, and seamlessly
  communication, collaboration, and competition between them.
- Playground & Testbed for C3 Capabilities: it provides a set of environments for evaluating and developing the
  **communication, collaboration, and competition**  (C3) capabilities of LLMs.

[//]: # (## Features)

[//]: # ()

[//]: # (- Support for multiple large language models.)

[//]: # (- Customizable language model-driven environments.)

[//]: # (- Easy-to-use API for efficient development.)

[//]: # (- Seamless interaction between humans and LLM agents.)

[//]: # (- Extensible design, allowing you to integrate additional models or environments.)

## Getting Started

### Prerequisites

- Python >= 3.7
- [OpenAI GPT-3](https://beta.openai.com/signup/) API key (optional, for using GPT-3 as an LLM agent)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/chat-arena/chat-arena
```

2. Install the package:

```bash
cd chat-arena
pip install .  # Install the package (which also installs the dependencies)
```

3. (Optional) To use GPT-3 as an LLM agent, set your OpenAI API key:

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

### Quick Multi-LLM Player Definition

```python
from chat_arena.agent import Player
from chat_arena.backend import OpenAIChat, Human, CohereChat

# Player 1: a "professor" agent played by OpenAI GPT-3.5-turbo 
player1 = Player(
    name="teacher",
    backend=OpenAIChat(...),
    role="You are a professor in ...")

# Player 2: a "student" agent played by a human
player2 = Player(
    name="student",
    backend=Human(...),
    role="You are a student who is interested in ...")

# Player 3: a "teaching assistant" agent played by Cohere
player3 = Player(
    name="teaching assistant",
    backend=CohereChat(...),
    role="You are a TA of module ...")
```

### Define a Language-Driven Environment

You can also create a language model-driven environment and add it to the Chat Arena:

```python
from chat_arena.environments.conversation import ModeratedConversation

env = ModeratedConversation(
    players=[player1.name, player2.name, player3.name],
    moderator_role="You are a teaching admin ...",
    moderator_backend=OpenAIChat(..),
env_description = "It is in a NLP classroom ...",
terminal_condition = "Has the student learned the basics of NLP?"
)
```

### Arena: a Playground to Run Language Games

Initialise Arena from scratch

```python
from chat_arena.arena import Arena

arena = Arena(
    players=[player1, ...],
    environment=env)
for _ in range(...):
    arena.print_status()
    arena.step()
```

Load Example Arenas

```python
arena = Arena.load("nlp-classroom")
arena.run(step=...)
```

Save Arena Gameplay History

```python
arena.save_history(fn=...)
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


