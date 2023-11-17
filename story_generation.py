from chatarena.agent import Player, Controller
from chatarena.backends import OpenAIChat
environment_description = "You are in a house in the winter countryside with no people around."
controller = Controller(name="Controller", backend=OpenAIChat(),
                        role_desc="You are the director of a popular play. Your job is to select the next actor that should go on stage.")
player1 = Player(name="Sheldon", backend=OpenAIChat(),
                 role_desc="You are a writer who has published many famous books and has many fans. You are thoughtful and friendly, and you love to read and write in general. You were saved by Annie and brought to her house after a car accident. Your leg was broken in a car accident and you need to be in a wheelchair.",
                 global_prompt=environment_description)
player2 = Player(name="Annie", backend=OpenAIChat(),
                 role_desc="You're a nurse with a penchant for murder and you are also an avid fan of Sheldon's books. When you learn that Sheldon has written the death of your favorite fictional character, Bitter, you imprison Sheldon in your own home and push him to write a book to keep Bitter alive.",
                 global_prompt=environment_description)
from chatarena.environments.conversation import Conversation
env = Conversation(player_names=[p.name for p in [player1, player2]])
from chatarena.arena import Arena
arena = Arena(players=[player1, player2],
              environment=env, global_prompt=environment_description)
arena.run(num_steps=10)
