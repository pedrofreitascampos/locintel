class ApplyMaskBase(object):
    def __init__(self):
        pass

    def apply_mask(self, *arg, **kwargs):
        raise NotImplementedError("Please implement in subclass")
