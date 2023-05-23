import re
import json

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True

def is_json_inside(text):
    text = re.sub('\s+', ' ', text)
    matches = re.findall(r'\{.*?\}', text)
    for match in matches:
        if is_json(match):
            return True
    return False

def extract_jsons(text):
    text = re.sub('\s+', ' ', text)
    matches = re.findall(r'\{.*?\}', text)
    parsed_jsons = []
    for match in matches:
        try:
            json_object = json.loads(match)
            parsed_jsons.append(json_object)
        except ValueError as e:
            pass
    return parsed_jsons


def extract_code(text):
    text = re.sub('```python', '```', text)
    matches = re.findall(r'```(.*?)```', text, re.DOTALL)
    parsed_codes = []
    for match in matches:
        parsed_codes.append(match)
    return parsed_codes


class AttributedDict(dict):
    """
    A dict class whose keys are automatically set as attributes of the class.
    Serializable to JSON.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError

    def __delattr__(self, key):
        del self[key]

    # check whether the key is string when adding the key
    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise ValueError("The key must be a string")
        super().__setitem__(key, value)

    def update(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).items():
            self[key] = value
