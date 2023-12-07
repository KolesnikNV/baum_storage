import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from db.engine import url_object
from db.models import Base

config = context.config
section = config.config_ini_section
config.set_section_option(section, "DATABASE_URL", os.environ.get("DATABASE_URL"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

url_object = url_object
target_metadata = Base.metadata

engine = engine_from_config(
    context.config.get_section(context.config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)

connection = engine.connect()

context.configure(
    connection=connection,
    target_metadata=target_metadata,
)


def run_migrations_offline():
    context.configure(url=url_object)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
