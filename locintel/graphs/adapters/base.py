from ..datamodel.jurbey import Jurbey


class BaseAdapter:
    """
    Defines adapter interface to all map formats
    """

    def __init__(self, metadata=None):
        self.G = Jurbey(metadata=metadata)

    def get_jurbey(self):
        raise NotImplementedError("Please implement subclass")
