import os
import sys
from pathlib import Path
from logging.config import fileConfig

# --- FIX: Add project root to Python's path ---
# This ensures that Alembic can find the 'app' module.
# IMPORTANT: Replace the path below with the actual absolute path to your project root.
PROJECT_ROOT = "/home/enzo/AI_Research_Platform" 
sys.path.insert(0, PROJECT_ROOT)
# --- END OF FIX ---

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import your Base from your models
# This will work now because we've adjusted the path above.
from app.models.project import Base

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load environment variables from .env
load_dotenv()

# Set the target_metadata to our Base for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = os.getenv("DATABASE_URL")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Get database URL from .env and set it in the config
    db_config = config.get_section(config.config_ini_section, {})
    db_config['sqlalchemy.url'] = os.getenv("DATABASE_URL")

    connectable = engine_from_config(
        db_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
