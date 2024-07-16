import os

import logging
import colorlog

DISCORD_TOKEN = 'BotToken' #here token for bot

# Setup logging configuration
def setup_logger(name, bot=None, channel_id=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Formatter für das Logging
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    # Farbiger Formatter für die Konsole
    color_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    # File Handler für die Protokolldatei
    file_handler = logging.FileHandler('bot.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Stream Handler für die Konsole
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(color_formatter)

    # Discord Handler für Fehlernachrichten
    if bot and channel_id:
        discord_handler = DiscordHandler(bot, channel_id)
        discord_handler.setLevel(logging.ERROR)
        discord_handler.setFormatter(formatter)
        logger.addHandler(discord_handler)

    # Hinzufügen der Handler zum Logger
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

class DiscordHandler(logging.Handler):
    def __init__(self, bot, channel_id):
        super().__init__()
        self.bot = bot
        self.channel_id = channel_id

    def emit(self, record):
        log_entry = self.format(record)
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            self.bot.loop.create_task(channel.send(f"```{log_entry}```"))

# Hauptlogger des Bots
logger = setup_logger('bot')
