<font size="+2" > 
<h1 align="center"> 🏟 <span style="color:coral">Chat Arena</span> </h1>
</font>
<h3 align="center">
    <p>Multi-Agent Language-Driven Environments for Large Language Models</p>
</h3>

---

Chat Arena is a Python library designed to facilitate interactions between multiple LLM-based agents in a
language-driven game environment. It provides the following features:

- Infrastructure for Multi-LLM Interaction: it enables rapid definition and creation of LLM-based agents, and seamlessly
  handles communication between them.
- Language-driven Game Environment: it provides a framework for creating a language-driven game environment, and a
  friendly UI to develop such games.
- Playground & Testbed for C3 Capabilities: it provides a set of environments for evaluating and developing the
  **communication, collaboration, and competition**  (C3) capabilities of LLMs.

## Features

- Support for multiple large language models.
- Customizable language model-driven environments.
- Easy-to-use API for efficient development.
- Seamless interaction between humans and LLM agents.
- Extensible design, allowing you to integrate additional models or environments.

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

[//]: # (## Usage)

[//]: # ()
[//]: # (Here's a simple example of how to use Chat Arena to create a conversation between a human and an LLM agent:)

[//]: # ()
[//]: # (```python)

[//]: # (from chat_arena import ChatArena, Human, LLM)

[//]: # ()
[//]: # (# Initialize the Chat Arena)

[//]: # (arena = ChatArena&#40;&#41;)

[//]: # ()
[//]: # (# Add a human participant)

[//]: # (human = Human&#40;name="Alice"&#41;)

[//]: # (arena.add_participant&#40;human&#41;)

[//]: # ()
[//]: # (# Add an LLM agent)

[//]: # (llm_agent = LLM&#40;name="GPT-3"&#41;)

[//]: # (arena.add_participant&#40;llm_agent&#41;)

[//]: # ()
[//]: # (# Start a conversation)

[//]: # (arena.start_conversation&#40;&#41;)

[//]: # ()
[//]: # (# Human sends a message)

[//]: # (human.send_message&#40;"Hello, how are you?"&#41;)

[//]: # ()
[//]: # (# LLM agent responds)

[//]: # (llm_agent.send_message&#40;"I'm doing great, thank you! How about you?"&#41;)

[//]: # ()
[//]: # (# Continue the conversation...)

[//]: # (```)

[//]: # ()
[//]: # (You can also create a language model-driven environment and add it to the Chat Arena:)

[//]: # ()
[//]: # (```python)

[//]: # (from chat_arena import ChatArena, Human, LLM, Environment)

[//]: # ()
[//]: # (# Initialize the Chat Arena)

[//]: # (arena = ChatArena&#40;&#41;)

[//]: # ()
[//]: # (# Add a human participant)

[//]: # (human = Human&#40;name="Alice"&#41;)

[//]: # (arena.add_participant&#40;human&#41;)

[//]: # ()
[//]: # (# Add an LLM agent)

[//]: # (llm_agent = LLM&#40;name="GPT-3"&#41;)

[//]: # (arena.add_participant&#40;llm_agent&#41;)

[//]: # ()
[//]: # (# Create a language model-driven environment)

[//]: # (env = Environment&#40;name="TriviaGame"&#41;)

[//]: # (arena.add_environment&#40;env&#41;)

[//]: # ()
[//]: # (# Start a conversation)

[//]: # (arena.start_conversation&#40;&#41;)

[//]: # ()
[//]: # (# Human sends a message)

[//]: # (human.send_message&#40;"Let's play a trivia game!"&#41;)

[//]: # ()
[//]: # (# Environment starts the trivia game)

[//]: # (env.send_message&#40;"Welcome to Trivia Game! Here's your first question: What is the capital of France?"&#41;)

[//]: # ()
[//]: # (# LLM agent responds)

[//]: # (llm_agent.send_message&#40;"The capital of France is Paris."&#41;)

[//]: # ()
[//]: # (# Environment evaluates the answer)

[//]: # (env.send_message&#40;"Correct! The capital of France is Paris. Next question: ..."&#41;)

[//]: # ()
[//]: # (# Continue the conversation and trivia game...)

[//]: # (```)

[//]: # ()
[//]: # (## Documentation)

[//]: # ()
[//]: # (For more detailed information on the available functions and classes, please refer to)

[//]: # (the [documentation]&#40;link-to-documentation&#41;.)

[//]: # ()
[//]: # (## Contributing)

[//]: # ()
[//]: # (We welcome contributions to improve and extend Chat Arena. Please follow these steps to contribute:)

[//]: # ()
[//]: # (1. Fork the repository.)

[//]: # (2. Create a new branch for your feature or bugfix.)

[//]: # (3. Commit your changes to the new branch.)

[//]: # (4. Create a pull request describing your changes.)

[//]: # (5. We will review your pull request and provide feedback or merge your changes.)

[//]: # ()
[//]: # (Please ensure your code follows the existing style and structure.)

[//]: # ()
[//]: # (## License)

[//]: # ()
[//]: # (Chat Arena is released under the [Apache License]&#40;LICENSE&#41;.)

[//]: # ()
[//]: # (## Contact)

[//]: # ()
[//]: # (If you have any questions or suggestions, feel free to open an issue or submit a pull request. You can also reach out to)

[//]: # (the maintainer at [chat-arena@gmail.com]&#40;mailto:chat-arena@gmail.com&#41;.)

[//]: # ()
[//]: # (Happy chatting!)


