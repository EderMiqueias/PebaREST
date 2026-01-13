import logging

default_handler = logging.StreamHandler()

def has_level_handler(logger: logging.Logger) -> bool:
    level = logger.getEffectiveLevel()
    current = logger

    while current:
        if any(handler.level <= level for handler in current.handlers):
            return True

        if not current.propagate:
            break

        current = current.parent

    return False


def create_logger(import_name: str, is_debug: bool) -> logging.Logger:
    logger = logging.getLogger(import_name)

    if is_debug and not logger.level:
        logger.setLevel(logging.DEBUG)

    if not has_level_handler(logger):
        logger.addHandler(default_handler)

    return logger
