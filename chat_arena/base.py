def sys_role_template(system_desc, role_desc, prompt_role="system"):
    system_prompts = [{"role": prompt_role, "content": system_desc},
                      {"role": prompt_role, "content": role_desc}]
    return system_prompts


class Agent:
    """Agent class that models generic agent behavior.
    This class is stateless and does not store any information about the game."""

    def __init__(self, role, system_desc, temperature, max_tokens):
        self.role = role
        self.sys_prompt = sys_role_template(system_desc, role, prompt_role="system")
        self.temperature = temperature
        self.max_tokens = max_tokens

    @property
    def name(self):
        raise NotImplementedError

    def get_response(self, history, temperature=None, max_tokens=None, stop=None):
        raise NotImplementedError

    @staticmethod
    def get_components(*args):
        raise NotImplementedError

    @staticmethod
    def parse_components(components, name, start_idx):
        raise NotImplementedError

    def step(self, arena, turn: int):
        raise NotImplementedError
