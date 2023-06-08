import os
import dotenv

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# IP = str(os.getenv("IP"))
# PGUSER = str(os.getenv("PGUSER"))
# PGPASS = str(os.getenv("PGPASS"))
# DATABASE = str(os.getenv("DATABASE"))
