from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

Env = Literal["dev", "test", "prod"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


def _package_version() -> str:
    try:
        return version("cicci-backend")
    except PackageNotFoundError:
        return "0.0.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    APP_NAME: str = "Cucina con Cicci API"
    APP_VERSION: str = Field(default_factory=_package_version)
    ENV: Env = "dev"
    DEBUG: bool | None = None
    LOG_LEVEL: LogLevel | None = None

    CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    DATABASE_URL: str | None = None

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def _defaults_from_env(self) -> "Settings":
        if self.DEBUG is None:
            self.DEBUG = self.ENV != "prod"
        if self.LOG_LEVEL is None:
            self.LOG_LEVEL = "DEBUG" if self.DEBUG else "INFO"
        return self

    @property
    def is_prod(self) -> bool:
        return self.ENV == "prod"


@lru_cache
def get_settings() -> Settings:
    return Settings()
