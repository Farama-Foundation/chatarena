import json
from manim import *
import sys
import textwrap
from manim import config
config.background_color = "#131416"
config.max_files_cached = 10000


name_to_color = {"Moderator": WHITE, "ModeratorA": GRAY_A}
color_list = [YELLOW, YELLOW_A, GREEN, GREEN_A, RED, RED_A]
def get_color(name):
    if name not in name_to_color:
        name_to_color[name] = color_list.pop()
        name_to_color[name+"A"] = color_list.pop()
    return name_to_color[name]
class Conversation(Scene):
    def get_formatted_text(self, data):
        return f"{data['name']}({data['turn']}): {data['text']}"

    def construct(self):
        with open(sys.argv[4], "r") as f:
            conversation_data = json.load(f)

        line_spacing = 0.6
        left_margin = 0.2
        bottom_margin = 0.2
        max_lines = 8
        current_line = 0
        prev_messages = VGroup()
        text_wrap_width = config["frame_width"] - 2  # Adjust to set the max text width

        conversation_list = []
        for obj in conversation_data:
            conversation_list.append(Text(font_size=25.0,text=obj.get('name')+"  ("+str(obj.get('turn'))+")",weight=BOLD,color=get_color(obj.get('name'))))
            text = textwrap.wrap(obj.get('text').replace(' ','  '), width=70)
            for t in text:
                conversation_list.append(Text(font_size=30.0,text=t,color=get_color(obj.get('name')+"A")))

        for message in conversation_list[0:20]:
            print(message.text)
            self.play(Write(message.align_on_border(LEFT).align_on_border(DOWN).shift(UP*bottom_margin).shift(RIGHT*left_margin)),run_time=0.7)
            prev_messages.add(message)
            self.play(Transform(prev_messages, prev_messages.copy().shift(UP*line_spacing)),run_time=0.4)
            for m in prev_messages:
                if m.is_off_screen():
                    self.remove(m)
                    prev_messages.remove(m)
            

        # for data in conversation_data:
        #     formatted_text = self.get_formatted_text(data)
        #     wrapped_text = "\n".join(textwrap.wrap(formatted_text, width=text_wrap_width, break_long_words=False))
        #     new_text_object = Text(wrapped_text, line_spacing=-0.5, width=text_wrap_width).scale(0.5)
        #     new_text_lines = len(wrapped_text.strip().split("\n"))
        #
        #     # Calculate the position of the new_text_object
        #     if current_line == 0:
        #         new_text_object.next_to(previous_texts, DOWN, buff=0).to_edge(UP, buff=0.5)
        #     else:
        #         new_text_object.next_to(previous_texts[-1], DOWN, aligned_edge=LEFT, buff=0.5)
        #     self.play(Write(new_text_object))
        #     previous_texts.add(new_text_object)
        #     current_line += new_text_lines
        #
        #     # If text exceeds max_lines, move it upward
        #     while current_line > max_lines:
        #         # Since we work only with one line at a time, we will always move the text by only one line
        #         lines_to_move = 1
        #
        #         self.play(previous_texts.animate.shift(UP * line_spacing))
        #         if len(previous_texts) >= 1:
        #             self.remove(previous_texts[0])
        #             previous_texts.remove(previous_texts[0])
        #         current_line -= lines_to_move

        self.wait()
