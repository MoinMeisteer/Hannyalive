import os
import sys
import logging


from dotenv import load_dotenv
from discord.ext import commands
from discord.flags import Intents

load_dotenv()
load_dotenv('.env')

LANGS_DIR = os.path.join(sys.path[0], 'langs')

os.environ.setdefault('BOT_COMMAND_PREFIX', '$')
os.environ.setdefault('DEFAULT_LANG', 'de')
os.environ.setdefault('SAVES_LIMIT', '16')
os.environ.setdefault('LOG_FILEPATH', 'debug.log')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('LOG_FORMAT', logging.BASIC_FORMAT)


assert os.getenv('SAVES_LIMIT').isdigit(), 'SAVES_LIMIT should be integer. '




intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=os.getenv('BOT_COMMAND_PREFIX'), intents=intents)