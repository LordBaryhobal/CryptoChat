class ANSI:
    CTRL = "\x1b["
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

    LBLACK = 90
    LRED = 91
    LGREEN = 92
    LYELLOW = 93
    LBLUE = 94
    LMAGENTA = 95
    LCYAN = 96
    LWHITE = 97

    BOLD = 1
    ITALIC = 3
    UNDERLINE = 4
    RESET = 0

    @staticmethod
    def build(styles: list[int]) -> str:
        return ANSI.CTRL + ";".join(map(str, styles)) + "m"
