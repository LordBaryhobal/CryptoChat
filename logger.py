import time

from ansi import ANSI


class Logger:
    def __init__(self, name: str = "", fmt: str = "[{time}][{name}/{level}] {message}", styles: dict[str, list[int]] = None):
        self.name: str = name
        self.fmt: str = fmt
        if styles is None:
            styles = {}
        self.styles: dict[str, list[int]] = styles

    def log(self, msg: str, level: str = "info") -> None:
        print(self.format(msg, level))

    def error(self, msg: str) -> None:
        self.log(msg, "error")

    def info(self, msg: str) -> None:
        self.log(msg, "info")

    def warn(self, msg: str) -> None:
        self.log(msg, "warning")

    def format(self, msg: str, level: str = "info") -> str:
        openingStyle = ANSI.build(self.styles.get(level, []))
        text = self.fmt.format(
            time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            name=self.name,
            level=level.upper(),
            message=msg
        )
        return openingStyle + text + ANSI.build([ANSI.RESET])


if __name__ == "__main__":
    logger = Logger(styles={
        "info": [ANSI.BLUE],
        "error": [ANSI.RED, ANSI.BOLD],
        "warning": [ANSI.YELLOW, ANSI.ITALIC],
        "success": [ANSI.LGREEN, ANSI.ITALIC],
        "link": [ANSI.LBLUE, ANSI.UNDERLINE]
    })

    logger.info("This is an informative message")
    logger.warn("This is an warning message")
    logger.error("This is an error message")
    logger.log("This is a success message", "success")
    logger.log("This is a link message", "link")
