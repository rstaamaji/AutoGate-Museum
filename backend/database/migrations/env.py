import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Import Base & Model kamu
from app.database import Base
from app.Models.User import User  # Wajib di-import agar terdeteksi
#from app.Models.Item import Item  # Wajib di-import jika ada

load_dotenv()

config = context.config
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))

if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
