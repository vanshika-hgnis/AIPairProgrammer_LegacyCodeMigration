import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

MODEL = os.getenv("MODEL")
API_KEY = os.getenv("OPENROUTER_API_KEY")

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": API_KEY,
    "Content-Type": "application/json",
  },
  data=json.dumps({
    "model": "meta-llama/llama-3.3-70b-instruct:free",
    "messages": [
        {
          "role": "user",
          "content": "What is the meaning of life?"
        }
      ]
  })
)

