# logger_core.py
import logging
from rich.logging import RichHandler
from rich.console import Console

console = Console()

def crear_logger(nombre_logger="mi_logger", nivel=logging.DEBUG):
    """
    Crea un logger con nombre propio, RichHandler y nivel configurable.
    """
    logger = logging.getLogger(nombre_logger)
    logger.setLevel(nivel)
    logger.propagate = False  # evita que los logs suban al root

    # Verifica si ya existe RichHandler
    if not any(isinstance(h, RichHandler) for h in logger.handlers):
        rich_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            markup=True,
            show_time=False,
            show_level=False,
            show_path=False
        )
        formatter = logging.Formatter("%(message)s")
        rich_handler.setFormatter(formatter)
        logger.addHandler(rich_handler)

    return logger