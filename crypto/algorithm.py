class Algorithm:
    NAME = ""

    def __init__(self, *args, **kwargs):
        ...

    def encode(self, *args, **kwargs) -> bytes:
        raise NotImplementedError

    def decode(self, *args, **kwargs) -> bytes:
        raise NotImplementedError

    @staticmethod
    def parseTaskKey(msg: str) -> int:
        raise NotImplementedError
