from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.text import Text
from rich.color import ANSI_COLOR_NAMES
import random

from ..arena import Arena, TooManyInvalidActions
from ..backends.human import HumanBackendError

ASCII_ART = r"""
_________  .__               __      _____                                   
\_   ___ \ |  |__  _____   _/  |_   /  _  \  _______   ____    ____  _____   
/    \  \/ |  |  \ \__  \  \   __\ /  /_\  \ \_  __ \W/ __ \  /    \ \__  \  
\     \____|   Y  \ / __ \_ |  |  /    |    \ |  | \/\  ___/ |   |  \ / __ \_
 \______  /|___|  /(____  / |__|  \____|__  / |__|    \___  >|___|  /(____  /
        \/      \/      \/                \/              \/      \/      \/ 
"""

visible_colors = [color for color in ANSI_COLOR_NAMES.keys() if
                  color not in ["black", "white", "red", "green"] and "grey" not in color]

MAX_STEPS = 5

import logging

# Set logging level to ERROR
logging.getLogger().setLevel(logging.ERROR)


class ArenaCLI:
    """
    The CLI user interface for ChatArena.
    """

    def __init__(self, arena: Arena):
        self.arena = arena

    def launch(self, max_steps: int = None, interactive: bool = True):
        """
        Run the CLI
        """
        if not interactive and max_steps is None:
            max_steps = MAX_STEPS

        console = Console()
        # Print ascii art
        console.print(ASCII_ART, style="bold dark_orange3")
        timestep = self.arena.reset()
        console.print("🏟 Chat Arena Initialized!", style="bold green")

        env = self.arena.environment
        players = self.arena.players

        env_desc = self.arena.global_prompt
        num_players = env.num_players
        player_colors = random.sample(visible_colors, num_players)  # sample different colors for players
        name_to_color = dict(zip(env.player_names, player_colors))
        # System and Moderator messages are printed in red
        name_to_color["System"] = "red"
        name_to_color["Moderator"] = "red"

        console.print(f"[bold green underline]Environment ({env.type_name}) description:[/]\n{env_desc}")

        # Print the player name, role_desc and backend_type
        for i, player in enumerate(players):
            player_name = Text(f"[{player.name} ({player.backend.type_name})] Role Description:")
            player_name.stylize(f"bold {name_to_color[player.name]} underline")
            console.print(player_name)
            console.print(player.role_desc)

        console.print("\n========= Arena Start! ==========\n", style="bold green")

        step = 0
        while not timestep.terminal:
            if interactive:
                command = prompt([('class:command', "command (n/r/q/s/h) > ")],
                                 style=Style.from_dict({'command': 'blue'}),
                                 completer=WordCompleter(
                                     ['next', 'n', 'reset', 'r', 'exit', 'quit', 'q', 'help', 'h', 'save', 's']))
                command = command.strip()

                if command == "help" or command == "h":
                    console.print("Available commands:")
                    console.print("    [bold]next or n or <Enter>[/]: next step")
                    console.print("    [bold]exit or quit or q[/]: exit the game")
                    console.print("    [bold]help or h[/]: print this message")
                    console.print("    [bold]reset or r[/]: reset the game")
                    console.print("    [bold]save or s[/]: save the history to file")
                    continue
                elif command == "exit" or command == "quit" or command == "q":
                    break
                elif command == "reset" or command == "r":
                    timestep = self.arena.reset()
                    console.print("\n========= Arena Reset! ==========\n", style="bold green")
                    continue
                elif command == "next" or command == "n" or command == "":
                    pass
                elif command == "save" or command == "s":
                    # Prompt to get the file path
                    file_path = prompt([('class:command', "save file path > ")],
                                       style=Style.from_dict({'command': 'blue'}))
                    file_path = file_path.strip()
                    # Save the history to file
                    self.arena.save_history(file_path)
                    # Print the save success message
                    console.print(f"History saved to {file_path}", style="bold green")
                else:
                    console.print(f"Invalid command: {command}", style="bold red")
                    continue

            try:
                timestep = self.arena.step()
            except HumanBackendError as e:
                # Handle human input and recover with the game update
                human_player_name = env.get_next_player()
                if interactive:
                    human_input = prompt(
                        [('class:user_prompt', f"Type your input for {human_player_name}: ")],
                        style=Style.from_dict({'user_prompt': 'ansicyan underline'})
                    )
                    # If not, the conversation does not stop
                    timestep = env.step(human_player_name, human_input)
                else:
                    raise e  # cannot recover from this error in non-interactive mode
            except TooManyInvalidActions as e:
                # Print the error message
                console.print(f"Too many invalid actions: {e}", style="bold red")
                break

            # The messages that are not yet logged
            messages = [msg for msg in env.get_observation() if not msg.logged]
            # Print the new messages
            for msg in messages:
                message_text = Text(f"[{msg.agent_name}->{msg.visible_to}]: {msg.content}")
                message_text.stylize(f"bold {name_to_color[msg.agent_name]}", 0,
                                     len(f"[{msg.agent_name}->{msg.visible_to}]:"))
                console.print(message_text)
                msg.logged = True

            step += 1
            if max_steps is not None and step >= max_steps:
                break

        console.print("\n========= Arena Ended! ==========\n", style="bold red")
