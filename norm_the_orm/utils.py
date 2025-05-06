import sys
import os
from loguru import logger


# Configure loguru
# Remove default handler
logger.remove()

log_level = os.environ.get('LOGLEVEL', 'DEBUG')

# Add a console handler with custom format
logger.add(
    sink=sys.stderr,
    format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
    level=log_level,
)


# Function to get a contextualized logger
def get_logger(name):
    """Returns a logger with the provided context name."""
    return logger.bind(name=name)
