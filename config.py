from dotenv import load_dotenv
import os

load_dotenv()


# config.py
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "nousresearch/hermes-3-llama-3.1-405b:free"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
