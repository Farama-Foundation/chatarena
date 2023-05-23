from chatarena.environments.base import Environment, TimeStep
from chatarena.message import Message, MessagePool
from typing import List, Dict, Union
from chatarena.agent import Player
from chatarena.backends import OpenAIChat
from chatarena.arena import Arena
from chatarena.utils import extract_code, extract_jsons
from io import StringIO
import sys
import traceback

class PythonREPL:
    """Simulates a standalone Python REPL."""
    def __init__(self):
        self.globals = {}

    def run(self, command: str) -> str:
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            exec(command, self.globals)
            sys.stdout = old_stdout
            output = mystdout.getvalue()
        except Exception:
            sys.stdout = old_stdout
            output = traceback.format_exc()
        return output


class IterativeCoding(Environment):
    type_name = "coding"

    def __init__(self, task:str=""):
        super().__init__(player_names=["coder", "verifier"])

        self.task = task
        # The "state" of the environment is maintained by the message pool
        self.message_pool = MessagePool()
        self.phase = "code" # "code", "verify", "iterate"
        self.python_repl = PythonREPL()
        self.max_turns = 10
        self._terminal = False
        self.reset()
        self.last_code = ""

    def get_next_player(self) -> str:
        if self.phase == "code":
            return "coder"
        elif self.phase == "iterate":
            return "coder"
        elif self.phase == "verify":
            return "verifier"

    def _moderator_speak(self, text: str, visible_to: Union[str, List[str]] = "all"):
        """
        moderator say something
        """
        message = Message(agent_name="Moderator", content=text, turn=self.turn, visible_to=visible_to)
        self.message_pool.append_message(message)

    def reset(self):
        self.turn = 0
        self.message_pool.reset()
        self._moderator_speak(f"For the following task \n ```{self.task}```. "
                              f"\n Write some testcases and then an actual function that implement the task. Everything should be in a single code block", visible_to="coder")
        observation = self.get_observation(self.get_next_player())
        self._terminal = False
        self.turn += 1
        return TimeStep(observation=observation, reward=self.get_zero_rewards(), terminal=self._terminal)

    def get_observation(self, player_name=None) -> List[Message]:
        if player_name is None:
            return self.message_pool.get_all_messages()
        else:
            return self.message_pool.get_visible_messages(player_name, turn=self.turn + 1)

    def process_broken(self):
        self._moderator_speak(f"The process is broken. Please restart the game.")
        self._terminal = True
        observation = self.get_observation(self.get_next_player())
        return TimeStep(observation=observation, reward=self.get_zero_rewards(), terminal=self._terminal)

    def step(self, player_name: str, action: str) -> TimeStep:
        assert player_name == self.get_next_player(), f"Wrong player! It is {self.get_next_player()} turn."
        visible_to = "all"
        message = Message(agent_name=player_name, content=action, turn=self.turn, visible_to=visible_to)
        self.message_pool.append_message(message)
        if self.phase in ["iterate", "code"]:
            code_list = extract_code(action)
            if len(code_list) != 1:
                return self.process_broken()
            self.last_code = code_list[0]
            interpreter_output = self.python_repl.run(code_list[0])
            self.phase = "verify"
        elif self.phase == "verify":
            json_list = extract_jsons(action)
            if len(json_list) != 1:
                return self.process_broken()
            if json_list[0]["result"] == "correct":
                self._terminal = True
                self._moderator_speak(f"Tests passed! Here's the code: \n ```{self.last_code}```")
                return TimeStep(observation=self.get_observation(self.get_next_player()),
                                reward=self.get_one_rewards(),
                                terminal=True)
            self.phase = "iterate"


        if self.phase == "verify":
            self._moderator_speak(f"Here's the outputs: {interpreter_output}. Is the code correct? Output with json format.",
                                  visible_to="verifier")
        elif self.phase == "iterate":
            self._moderator_speak(f"Now iterate your code with feedbacks. First think about why and then write the new code.", visible_to="coder")

        self.turn += 1
        return TimeStep(observation=self.get_observation(self.get_next_player()),
                        reward=self.get_zero_rewards(),
                        terminal=self._terminal)


if __name__ == "__main__":
    coder_role_description = """
    You are a coder. You are going to follow a workflow of coding to implement a specific function.
    Your implementation will be tested by the verifier. If the implementation is wrong, you will try output new implementation given the feedback.
    Your output can include your reasoning process but the code part should always be surrounded by triple backticks.
    """

    verifier_role_description = """
    You are a verifier. You are going to verify if the code is correct or not according to the interpretor outputs.
    You should always output a json with following format:
    { 
    "outputs_extraction": the outputs from the interpreter output showing the error or correctness of the code,
    "result": "correct" or "incorrect",
    }
    """

    task = """
    Write a python function for detecting if there's a json within a bunch of text.
    The input of this function is a string, and the output is a boolean.
    If there are multiple jsons in the string, return True if any of them is valid.
    """

    coder = Player("coder", role_desc=coder_role_description,
                   backend=OpenAIChat(max_tokens=1024, model="gpt-4"))
    verifier = Player("verifier", role_desc=verifier_role_description,
                        backend=OpenAIChat(max_tokens=1024, model="gpt-4"))
    env = IterativeCoding(task=task)
    arena = Arena([coder, verifier], env)
    arena.launch_cli()
