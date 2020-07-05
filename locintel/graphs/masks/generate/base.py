class BaseMaskGenerator:
    def __init__(self, name="base"):
        self.name = name

    def generate(self, *arg, **kwargs):
        raise NotImplementedError("Please implement subclass")
