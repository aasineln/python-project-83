import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/app")
    secret_key: str = os.getenv(
        "SECRET_KEY", "dev-secret-key-change-in-production"
    )
    debug: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 5000))
    max_url_length: int = 255
    templates_auto_reload: bool = debug

    @classmethod
    def from_env(cls) -> "Config":
        return cls()

    @property
    def is_production(self) -> bool:
        return not self.debug


class DevelopmentConfig(Config):
    debug: bool = True
    templates_auto_reload: bool = True


class ProductionConfig(Config):
    debug: bool = False

    @classmethod
    def from_env(cls) -> "ProductionConfig":
        if not os.getenv("SECRET_KEY"):
            raise ValueError("SECRET_KEY must be set in production")
        if not os.getenv("DATABASE_URL"):
            raise ValueError("DATABASE_URL must be set in production")
        return cls()


class TestingConfig(Config):
    testing: bool = True
    database_url: str = "sqlite:///:memory:"


def get_config() -> Config:
    env = os.getenv("FLASK_ENV", "development")

    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    config_class = configs.get(env, DevelopmentConfig)
    return config_class.from_env()
