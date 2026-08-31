import os
from dotenv import load_dotenv


load_dotenv()


class Config:

    DATABASE_URL = os.getenv("DATABASE_URL")

    DEBUG = True

    APP_NAME = "Smart Waste Management System"