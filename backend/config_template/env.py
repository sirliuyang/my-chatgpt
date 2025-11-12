import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from src.db.base import Base

# === 第一步：加载 .env 文件 ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # alembic/
ENV_PATH = os.path.join(BASE_DIR, "..", "src", ".env")  # → 项目根/src/.env

if not os.path.exists(ENV_PATH):
    raise RuntimeError(f".env 文件未找到: {ENV_PATH}")

load_dotenv(dotenv_path=ENV_PATH)

# === 第二步：获取 Alembic 配置 ===
config = context.config

# === 第三步：动态设置数据库 URL（关键！）===
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL 未在 .env 中配置！请检查 .env 文件。")
config.set_main_option("sqlalchemy.url", db_url)

# === 第四步：原有配置必须保留！===
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# === 第五步：导入你的模型 ===
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.user import User

target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
