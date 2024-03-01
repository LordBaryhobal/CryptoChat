class Algorithm:
    def __init__(self):
        ...

    def encode(self, *args, **kwargs) -> bytes:
        raise NotImplementedError

    def decode(self, *args, **kwargs) -> bytes:
        raise NotImplementedError
