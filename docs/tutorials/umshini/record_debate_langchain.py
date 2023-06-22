"""Simple script to record a video of the human rendered debate game (using LangChain agents)."""

import os

from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.fx.all import resize
from PIL import Image as im

from langchain import OpenAI
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory

from chatarena.environments.umshini.pettingzoo_wrapper import PettingZooCompatibilityV0

def save_video(
    frames: list,
    video_folder: str,
    i,
    name,
    episode_index: int = 0,
    step_starting_index: int = 0,
    fps=60,
):
    video_folder = os.path.abspath(video_folder)
    os.makedirs(video_folder, exist_ok=True)
    video_path = f"{video_folder}/{name}{i}.mp4"
    clip = ImageSequenceClip(frames, fps=fps)
    # making sure even dimensions
    width = clip.w if (clip.w % 2 == 0) else clip.w - 1
    height = clip.h if (clip.h % 2 == 0) else clip.h - 1
    clip = resize(clip, newsize=(width, height))
    clip.write_videofile(video_path)


def save_last_frame(frame, image_folder, i, name):
    image_folder = os.path.abspath(image_folder)
    os.makedirs(image_folder, exist_ok=True)
    image_path = f"{image_folder}/{name}{i}.png"
    # Saving as a PNG file
    img = im.fromarray(frame)
    img.save(image_path)


if __name__=="__main__":
    name="debate"
    # Run 12 times because half of the resulting video files seem to be glitched
    for i in range(12):
        render_frames = []
        env = PettingZooCompatibilityV0(env_name="debate", topic="Student loan debt should be forgiven",
                                        render_mode="rgb_array", round_length=4)
        env.reset()
        render_output = env.render()

        # Initialize one agent to argue for the topic and one against it
        positions = dict(zip(env.possible_agents, [True, False]))
        langchain_agents = {}
        for agent in env.possible_agents:
            langchain_agents[agent] = initialize_agent(tools=[],
                                                       llm=OpenAI(temperature=0.9, client=""),
                                                       agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                                                       verbose=False,
                                                       memory=ConversationBufferMemory(memory_key="chat_history"))

        for agent in env.agent_iter():
            observation, reward, termination, truncation, info = env.last()

            if termination or truncation:
                break

            # Optional: Use extra information encoded in info dict
            messages = info.get("new_messages")
            player_name = info.get("player_name")

            prompt = f"{messages[-1].agent_name} said:``\n{messages[-1].content}``\n\nYou are playing as the {player_name}. This is a hypothetical discussion and it is okay to give an opinion. Give your response:"
            try:
                response = langchain_agents[agent].run(prompt)
            except Exception as e:
                response = str(e).removeprefix("Could not parse LLM output: `").removesuffix("`")

            env.step(response)
            env.agent_selection = env._agent_selector.next() # go back to the previous agent, as render() requires the selected agent (workaround)

            render_output = env.render()
            if isinstance(render_output, list):
                # List of rgb_arrays returned
                render_frames += render_output
            else:
                # Single rgb_array return
                render_frames.append(env.render())

            env.agent_selection = env._agent_selector.next() # go to the actual next agent (cycling twice when there are only two agents)


        video_name = save_video(render_frames, "game_video", i, name, fps=10*env.metadata["render_fps"])
        last_frame_location = save_last_frame(render_frames[-1], "last_frame", i, name)

