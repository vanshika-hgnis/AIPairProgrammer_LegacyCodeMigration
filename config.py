from dotenv import load_dotenv
import os

load_dotenv()


# config.py
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "mistralai/mixtral-8x7b"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
