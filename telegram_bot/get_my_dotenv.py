import os
# Load .env file using:

from dotenv import load_dotenv
load_dotenv()

# Use the variable with:
print(os.getenv('TELEGRAM_TOKEN'))

