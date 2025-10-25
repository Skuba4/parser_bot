import os
from dotenv import load_dotenv

load_dotenv()

DOWNLOAD_PATH = 'downloads'
MAX_FOLDER_SIZE = 1 * 1024 * 1024 * 1024  # 1 ГБ

TOKEN = os.getenv("TOKEN")