import os
import sys
from dotenv import load_dotenv

# Define the base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the base directory to the system path to ensure modules can be imported
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Load environment variables from the .env file located at the project root
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Any other global bootstrapping logic can be added here
from config.paths import PRIVATE_DISK, PUBLIC_DISK

# Ensure compulsory directories exist
# We use str() to ensure compatibility and exist_ok=True to avoid errors if they already exist
os.makedirs(os.path.join(str(PRIVATE_DISK), "uploads"), exist_ok=True)
os.makedirs(os.path.join(str(PUBLIC_DISK), "pdfs"), exist_ok=True)

print(f"Bootstrapping complete. Storage paths verified.")
