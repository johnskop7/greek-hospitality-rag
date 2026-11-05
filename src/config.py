import os
from dotenv import load_dotenv

load_dotenv()  # reads .env from the current folder into environment variables

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")

if __name__ == "__main__":
    # Never print the key itself, only whether it's set
    print("API key set:", bool(LLM_API_KEY))
    print("Model:", LLM_MODEL)