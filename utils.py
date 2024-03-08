import os


def formatException(ex: Exception) -> str:
    """
    Formats the given exception in a pretty and concise string
    Args:
        ex: the exception to format

    Returns:
        the formatted exception
    """

    tree = []
    tb = ex.__traceback__

    while tb is not None:
        filename = relpath(tb.tb_frame.f_code.co_filename)
        lineno = tb.tb_lineno
        tree.append(f"{filename}:{lineno}")
        tb = tb.tb_next

    return f"Exception: {ex} ({' -> '.join(tree)})"


def relpath(path: str) -> str:
    """
    Computes the path relative to the project root equivalent to the given path
    Args:
        path: the path to relativize

    Returns:
        the path relative to the project root
    """

    return os.path.relpath(path, getRootPath())

def getRootPath() -> str:
    """
    Returns the root project path
    Returns:
        the path of the project directory
    """
    return os.path.dirname(os.path.realpath(__file__))