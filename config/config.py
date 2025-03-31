import os
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

class Config:
    MYSQL = {
        "host": os.getenv("MYSQL_HOST"),
        "port": int(os.getenv("MYSQL_PORT")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DB"),
    }

    # MONGODB = {
    #     "host": os.getenv("MONGO_HOST"),
    #     "port": int(os.getenv("MONGO_PORT")),
    #     "database": os.getenv("MONGO_DB"),
    # }

    LLAMA_MODEL_NAME = os.getenv("LLAMA_MODEL_NAME")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
