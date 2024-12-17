import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
DB_DNS = os.getenv("DB_DSN")

SUBSCRIPTION_CHANNEL_ID = -1001682634667
