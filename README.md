<!--
  Title: Chat Arena
  Description: Chat Arena (or ChatArena) is a language game environment for Large Language Models (LLMs) like GPT-3, GPT-4, ChatGPT, etc.
  Author: Yuxiang Wu
  -->

<h1 align="center"> 🏟 <span style="color:orange"><a href="https://www.chatarena.org/">ChatArena</a></span> </h1>

<h3 align="center">
    <p>Multi-Agent Language Game Environments for LLMs</p>
</h3>


[![License: Apache2](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://github.com/chatarena/chatarena/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/chatarena)](https://pypi.org/project/chatarena/)
[![Python 3.9+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![twitter](https://img.shields.io/twitter/follow/_chatarena?style=social&label=Follow%20ChatArena)](https://twitter.com/_chatarena)
[![slack](https://img.shields.io/badge/Slack-join-blueviolet?logo=slack&amp)](https://join.slack.com/t/chatarena/shared_invite/zt-1t5fpbiep-CbKucEHdJ5YeDLEpKWxDOg)
[![Open In Colab](https://img.shields.io/badge/Colab-Open%20Notebook-blue?logo=google-colab)](https://colab.research.google.com/drive/1vKaskNMBtuGOVgn8fQxMgjCevn2wp1Ml?authuser=0#scrollTo=P5DCC0Y0Zbxi)

---

ChatArena is a library that provides multi-agent language game environments and facilitates research about autonomous
LLM agents and their social interactions.
It provides the following features:

- **Abstraction**: it provides a flexible framework to define multiple players, environments and the interactions
  between them, based on Markov Decision Process.
- **Language Game Environments**: it provides a set of environments that can help understanding, benchmarking or
  training agent LLMs.
- **User-friendly Interfaces**: it provides both Web UI and CLI to develop/prompt engineer your LLM agents to act in
  environments.

![ChatArena Architecture](docs/images/chatarena_architecture.png)

## Getting Started

**Try our online demo:**
[![demo](https://img.shields.io/badge/Demo-Huggingface%F0%9F%A4%97%20Space-orange?style=flat)](https://chatarena-chatarena-demo.hf.space)
[![Demo video](https://img.shields.io/badge/Video-Vimeo-blue?logo=vimeo)](https://vimeo.com/816979419)

### Installation

Requirements:

- Python >= 3. 7
- OpenAI API key (optional, for using GPT-3.5-turbo or GPT-4 as an LLM agent)

Install with pip:

```bash
pip install chatarena
```

or install from source:

```bash
pip install git+https://github.com/chatarena/chatarena
```

To use GPT-3 as an LLM agent, set your OpenAI API key:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

#### Optional Dependencies

By default `pip install chatarena` will only install dependencies necessary for ChatArena's core functionalities.
You can install optional dependencies with the following commands:
```bash
pip install chatarena[all_backends] # install dependencies for all supported backends: anthropic, cohere, huggingface, etc.
pip install chatarena[all_envs]     # install dependencies for all environments, such as pettingzoo
pip install chatarena[all]          # install all optional dependencies for full functionality
```

### Launch the Demo Locally

The quickest way to see ChatArena in action is via the demo Web UI.
To launch the demo on your local machine, you first pip install chatarena with extra gradio dependency, then git clone
this repository to your local folder, and finally call the `app.py` in the root directory of the repository:

```shell
pip install chatarena[gradio]
git clone https://github.com/chatarena/chatarena.git
cd chatarena
gradio app.py
```

This will launch a demo server for ChatArena, and you can access it from your browser (port 8080).

[//]: # (The interface looks like this:)

[//]: # (![webui screenshot]&#40;docs/images/webui.png&#41;)

Check out this video to learn how to use Web UI: [![Webui demo video](https://img.shields.io/badge/WebUI%20Demo%20Video-Vimeo-blue?logo=vimeo)](https://vimeo.com/816979419)

## For Developers

For an introduction to the ChatArena framework, please refer to [this document](docs/devdoc/design.md).
For a walkthrough of building a new environment, check [![Open In Colab](https://img.shields.io/badge/Colab-Open%20Notebook-blue?logo=google-colab)](https://colab.research.google.com/drive/1vKaskNMBtuGOVgn8fQxMgjCevn2wp1Ml?authuser=0#scrollTo=P5DCC0Y0Zbxi)

Here we provide a compact guide on minimal setup to run the game and some general advice on customization.

### Key Concepts

1. **Arena**: Arena encapsulates an environment and a collection of players. It drives the main loop of the game and
   provides HCI utilities like webUI, CLI, configuration loading and data storage.
2. **Environment**: The environment stores the game state and executes game logics to make transitions between game
   states. It also renders observations for players, the observations are natural languages.
    1. The game state is not directly visible to the players. Players can only see the observations.
3. **Language Backend**: Language backends are the source of language intelligence. It takes text (or collection of
   text) as input and returns text in response.
4. **Player**: The player is an agent that plays the game. In RL terminology, it’s a policy, a stateless function
   mapping from observations to actions.

### Run the Game with Python API

Load `Arena` from a config file -- here we use `examples/nlp-classroom-3players.json` in this repository as an example:

```python
arena = Arena.from_config("examples/nlp-classroom-3players.json")
arena.run(num_steps=10)
```

Run the game in an interactive CLI interface:

```python
arena.launch_cli()
```

Check out this video to learn how to use
CLI: [![cli demo video](https://img.shields.io/badge/CLI%20Demo%20Video-Vimeo-blue?logo=vimeo)](https://vimeo.com/816989884)
A more detailed guide about how to run the main interaction loop with finer-grained control can be
found [here](docs/devdoc/mainloop.md)

### General Customization Advice

1. **Arena**: Overriding Arena basically means one is going to write their own main loop. This can allow different
   interaction interfaces or drive games in a more automated manner, for example, running an online RL training loop
2. **Environment**: A new environment corresponds to a new game, one can define the game dynamics here with hard-coded
   rules or a mixture of rules and language backend.
3. **Backend**: If one needs to change the way of formatting observations (in terms of messages) into queries for the
   language model, the backend should be overridden.
4. **Player**: By default, when a new observation is fed, players will query the language backend and return the
   response as actions. But one can also customize the way that players are interacting with the language backend.

### Creating your Custom Environment

You can define your own environment by extending the `Environment` class. Here are the general steps:

1. Define the class by inheriting from a base class and setting `type_name`, then add the class
   to [`ALL_ENVIRONMENTS`](chatarena/environments/__init__.py#L17)
2. Initialize the class by defining `__init__` method (its arguments will define the corresponding config) and
   initializing class attributes
3. Implement game mechanics in methods `step`
4. Handle game states and rewards by implementing methods such as `reset`, `get_observation`, `is_terminal`,
   and `get_rewards`
5. Develop role description prompts (and a global prompt if necessary) for players using CLI or Web UI and save them to
   a
   config file.

We provide [a detailed tutorial](docs/tutorials/create_your_environment.md) to demonstrate how to define a custom
environment,
using the [`Chameleon` environment](chatarena/environments/chameleon.py) as example.

If you want to port an existing library's environment to ChatArena, check
out [`PettingzooChess` environment](chatarena/environments/pettingzoo_chess.py) as an example.

## List of Environments

### [Conversation](chatarena/environments/conversation.py)

A multi-player language game environment that simulates a
conversation.

* [NLP Classroom](examples/nlp-classroom-3players.json): a 3-player language game environment that simulates a
  classroom
  setting. The game is played in turns, and each turn a player can either ask a question or answer a question.
  The game ends when all players have asked and answered all questions.

### [Moderator Conversation](chatarena/environments/conversation.py)

Based on converstion, but with a moderator that controls the game dynamics.

* [Rock-paper-scissors](examples/rock-paper-scissors.json): a 2-player language game environment that simulates a
  rock-paper-scissors game with moderator conversation.
  Both player will act in parallel, and the game ends when one player wins 2 rounds.
* [Tic-tac-toe](examples/tic-tac-toe.json): a 2-player language game environment that simulates a tic-tac-toe
  game with moderator conversation.
  The game is played in turns, and each turn a player can either ask for a move or make a move. The game ends when
  one
  player wins or the board is full.

### [Chameleon](chatarena/environments/chameleon.py)

A multi-player social deduction game. There are two roles in the game, chameleon and non-chameleon.
The topic of the secret word will be first revealed to all the players.
Then the secret word will be revealed to non-chameleons.
The chameleon does not know the secret word.
The objective in the game depends on the role of the player:

- If you are not a chameleon, your goal is to reveal the chameleon without exposing the secret word.
- If you are a chameleon, your aim is to blend in with other players, avoid being caught, and figure out the secret
  word.
  There are three stages in the game:

1. The giving clues stage: each player will describe the clues about the secret word.
2. The accusation stage: In this stage, each player will vote for another player who is most likely the chameleon. The
   chameleon should vote for other players.
3. The guess stage: If the accusation is correct, the chameleon should guess the secret word given the clues revealed by
   other players.

### [PettingZooChess](chatarena/environments/pettingzoo_chess.py)

A two-player chess game environment that uses the PettingZoo Chess environment.

### [PettingZooTicTacTeo](chatarena/environments/pettingzoo_tictactoe.py)

A two-player tic-tac-toe game environment that uses the PettingZoo TicTacToe environment. Differing from the
`Moderator Conversation` environment, this environment is driven by hard-coded rules rather than a LLM moderator.

## Contributing

We welcome contributions to improve and extend ChatArena. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes to the new branch.
4. Create a pull request describing your changes.
5. We will review your pull request and provide feedback or merge your changes.

Please ensure your code follows the existing style and structure.

## Citation

If you find ChatArena useful for your research, please cite our repository (our arxiv paper is coming soon):

```bibtex
@software{ChatArena,
  author = {Yuxiang Wu, Zhengyao Jiang, Akbir Khan, Yao Fu, Laura Ruis, Edward Grefenstette, and Tim Rocktäschel},
  title = {ChatArena: Multi-Agent Language Game Environments for Large Language Models},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  version = {0.1},
  howpublished = {\url{https://github.com/chatarena/chatarena}},
}
```

## Contact

If you have any questions or suggestions, feel free to open an issue or submit a pull request.
You can also follow us on [Twitter](https://twitter.com/_chatarena) or
join [our Slack channel](https://join.slack.com/t/chatarena/shared_invite/zt-1t5fpbiep-CbKucEHdJ5YeDLEpKWxDOg)
to get the latest updates.

Happy chatting!

## Sponsors

We would like to thank our sponsors for supporting this project:

- [SEQUOIA](https://www.sequoiacap.com/)
- [Shixiang Capital](https://sx.shixiangcap.com/home) 

