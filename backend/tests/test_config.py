import pytest
from pydantic import ValidationError

from app.config import Settings


def _settings(**kwargs: object) -> Settings:
    return Settings(_env_file=None, **kwargs)  # type: ignore[arg-type]


def test_defaults_dev() -> None:
    s = _settings()
    assert s.ENV == "dev"
    assert s.DEBUG is True
    assert s.LOG_LEVEL == "DEBUG"
    assert s.is_prod is False


def test_prod_defaults_safe() -> None:
    s = _settings(ENV="prod")
    assert s.DEBUG is False
    assert s.LOG_LEVEL == "INFO"
    assert s.is_prod is True


def test_explicit_debug_wins_over_env() -> None:
    s = _settings(ENV="prod", DEBUG=True)
    assert s.DEBUG is True


def test_cors_origins_from_csv() -> None:
    s = _settings(CORS_ORIGINS="http://a.test, http://b.test ,")
    assert s.CORS_ORIGINS == ["http://a.test", "http://b.test"]


def test_cors_origins_from_list() -> None:
    s = _settings(CORS_ORIGINS=["http://a.test"])
    assert s.CORS_ORIGINS == ["http://a.test"]


def test_invalid_env_rejected() -> None:
    with pytest.raises(ValidationError):
        _settings(ENV="staging")


def test_explicit_log_level_wins_over_env() -> None:
    s = _settings(LOG_LEVEL="INFO")
    assert s.LOG_LEVEL == "INFO"
