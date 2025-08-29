from dotenv import load_dotenv
import logging
from enum import Enum


class ModelProvider(str, Enum):
    GOOGLE_GENAI = "google_genai"
    OLLAMA = "ollama"


class GoogleGenAIModel(str, Enum):
    GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro"


class OllamaModel(str, Enum):
    GEMMA_3_8B = "gemma-3:8b"
    QWEN_3_8B = "qwen-3:8b"


def load_config(dotenv_path=".env"):
    """
    Loads environment variables from a .env file using python-dotenv.

    Args:
        dotenv_path (str): Path to the .env file. Defaults to ".env".

    Returns:
        bool: True if the .env file was loaded successfully, False otherwise.
    """
    try:
        load_dotenv(dotenv_path)
        return True
    except Exception as e:
        logging.error(f"Error loading .env file: {e}")
        return False
