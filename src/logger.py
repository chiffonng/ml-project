import logging
import os
from datetime import datetime

LOG_FILE = f"{datetime.now().strftime('%Y-%m-%d')}.log"
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE)

# create logs directory if not exists
if not os.path.exists("logs"):
    os.mkdir("logs")

logging.basicConfig(
    filename=LOG_FILE_PATH,
    filemode='w',
    format="[%(asctime)s] %(lineno)d - %(name)s - %(levelname)s - %(message)s",
    level = logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)