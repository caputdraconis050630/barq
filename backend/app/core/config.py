import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Barq"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"

settings = Settings()
