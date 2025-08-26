from dotenv import load_dotenv


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
        print(f"Error loading .env file: {e}")
        return False
