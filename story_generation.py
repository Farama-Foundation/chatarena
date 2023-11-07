from chatarena.agent import Player
from chatarena.backends import OpenAIChat
environment_description = "You are in an empty house."
player1 = Player(name="Dick", backend=OpenAIChat(),
                 role_desc="You are Dick, an intelligent, witty, sexually attractive man with a dark side: a short temper, a control freak, maybe even a paranoid one. You're married to Jane and have a three-year-old daughter, Nell, and verbally abuse and mistreat Jane because you suspect Jane of cheating on you. Jane gets a divorce because she can't take it anymore and gets custody of her daughter. After a horrific incident, you are arrested and sent to jail.",
                 global_prompt=environment_description)
player2 = Player(name="Jane", backend=OpenAIChat(),
                 role_desc="You are Jane and you notice a faint, faded odor of Vitamin Conditioner in the house, it is Dick's Conditioner. You sit in a chair, your muscles too flaccid with fear to stand up. As you hear Dick's footsteps begin to descend the stairs, you think: Even in prison, only Dick would have made sure he had conditioner. You have to get up, you have to run, but you can't move.",
                 global_prompt=environment_description)
from chatarena.environments.conversation import Conversation
env = Conversation(player_names=[p.name for p in [player1, player2]])
from chatarena.arena import Arena
arena = Arena(players=[player1, player2],
              environment=env, global_prompt=environment_description)
arena.run(num_steps=10)
