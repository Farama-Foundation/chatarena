import json

from chatarena.agent import Player, Controller
from chatarena.backends import OpenAIChat
from chatarena.environments import Story
from chatarena.arena import Arena

environment_description = "You are in a house in the winter countryside with no people around."
controller = Controller(name="Controller", backend=OpenAIChat(),
                        role_desc="You are the scene coordinator of a popular play. Your job is to select the next actor that should go on stage. You will be given several rounds of previous conversation in the play. If you think a player should be on stage next, print the player's name. For example: 'Next: Amy' or 'Next: Sheldon'. If you think the scene should end, then print 'Next: END'.",
                        global_prompt="The players are Annie and Sheldon. If no previous rounds are provided, generate the first player on stage.")
designer = Player(name="Designer", backend=OpenAIChat(),
                  role_desc=f"You are the designer of a popular play. Your job is to design a setting for this play. The topic of your play is '{environment_description}'. Please compose a SHORT setting that eloborate more details about the background, but don't mention information about the main characters..")
player1 = Player(name="Sheldon", backend=OpenAIChat(),
                 role_desc="You are a writer who has published many famous books and has many fans. You are thoughtful and friendly, and you love to read and write in general. You were saved by Annie and brought to her house after a car accident. Your leg was broken in a car accident and you need to be in a wheelchair.",
                 global_prompt=environment_description)
player2 = Player(name="Annie", backend=OpenAIChat(),
                 role_desc="You're a nurse with a penchant for murder and you are also an avid fan of Sheldon's books. When you learn that Sheldon has written the death of your favorite fictional character, Bitter, you imprison Sheldon in your own home and push him to write a book to keep Bitter alive.",
                 global_prompt=environment_description)
writer = Player(name="Writer", backend=OpenAIChat(),
                 role_desc="You're the writer of a popular play. Your job is to write the play given several rounds of previous conversation between the characters.",
                 global_prompt=environment_description)
players = [controller, designer, player1, player2, writer]

env = Story(player_names=[p.name for p in players])
# arena = Arena.from_config('story_generation.json')
arena = Arena(players=players,
              environment=env, global_prompt=environment_description)
# json.dump(arena.to_config(), open('story_generation.json', 'w'))
arena.run(num_steps=6)
