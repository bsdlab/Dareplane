from dareplane_utils.logging.logger import get_logger

# Adding a separate console handler is good for working with the module in isolation
# when using it in combination with other modules and a centralized logging server,
# you might want to turn this off to avoid duplicated log values.
logger = get_logger("strawman", add_console_handler=True)
