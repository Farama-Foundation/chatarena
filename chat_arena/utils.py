class AttributeDict(dict):
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
