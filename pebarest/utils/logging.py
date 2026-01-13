import logging


class PebaColoredFormatter(logging.Formatter):
    """Formatador com cores ANSI para o terminal."""

    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    # O formato base: Data | Nivel | Modulo | Mensagem
    format_str = "[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


default_handler = logging.StreamHandler()
default_handler.setFormatter(PebaColoredFormatter())

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
