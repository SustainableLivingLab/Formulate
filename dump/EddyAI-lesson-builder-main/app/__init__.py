import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
from flask import Flask
from .config import Config

# Setup logger
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file = 'logs/' + datetime.datetime.now().strftime("%Y-%m-%d") + '-app.log'
log_file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=30)
log_file_handler.setFormatter(log_formatter)

# Initialize app
app = Flask(__name__)
app.config.from_object(Config)
app.json.sort_keys = False
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(log_file_handler)

from app import routes
