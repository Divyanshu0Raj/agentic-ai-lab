import os

from dotenv import load_dotenv

load_dotenv()

def get_groq_config() -> tuple[str,str]:

    api_key=os.getenv("GROQ_API_KEY")
    model=os.getenv("GROQ_MODEL")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. add it to your .env file"

        )

    return api_key,model