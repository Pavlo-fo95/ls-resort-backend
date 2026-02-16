from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
import sys
from pathlib import Path

# чтобы импорты app.* работали, если alembic запускается из корня проекта
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))  # лучше чем append()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# импортируем Base и МОДЕЛИ (важно, чтобы модель загрузилась)
from app.database import Base
from app.models import ContactMessage, ServiceItem, Review  # или просто import app.models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_as_batch=True,  # полезно для SQLite (ALTER через batch)
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
