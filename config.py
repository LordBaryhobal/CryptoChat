import json
import os

from utils import getRootPath


class Config:
    THEME = "auto"
    HOST = ""
    PORT = 0
    _path = os.path.join(getRootPath(), "config.json")

    @staticmethod
    def _load() -> None:
        if not os.path.isfile(Config._path):
            return

        with open(Config._path, "r") as f:
            config = json.load(f)

        Config.THEME = config.get("theme", Config.THEME)
        Config.HOST = config.get("host", Config.HOST)
        Config.PORT = config.get("port", Config.PORT)

    @staticmethod
    def save() -> None:
        with open(os.path.join(getRootPath(), "config.json"), "w") as f:
            json.dump({
                "theme": Config.THEME,
                "host": Config.HOST,
                "port": Config.PORT
            }, f, indent=4)


Config._load()
