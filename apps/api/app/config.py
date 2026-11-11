from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / '.env', extra='ignore')
    app_env: Literal['development', 'test', 'production'] = 'development'
    public_origin: str = 'http://localhost:3000'
    database_url: str
    media_backend: Literal['local'] = 'local'
    media_root: Path = ROOT / '.data/media'
    csrf_secret: str
    abuse_hmac_secret: str
    session_absolute_seconds: int = 43200
    session_idle_seconds: int = 3600
    trusted_proxy_cidrs: str = ''
    contact_retention_days: int = 180
    contact_ip_limit: int = 5
    contact_site_limit: int = 100
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    contact_notify_to: str | None = None
    log_level: str = 'INFO'

    @field_validator('database_url')
    @classmethod
    def postgres_driver(cls, value: str) -> str:
        # Managed providers return generic PostgreSQL URLs; use our pinned psycopg3 driver.
        for prefix in ('postgres://', 'postgresql://'):
            if value.startswith(prefix):
                return 'postgresql+psycopg://' + value[len(prefix):]
        return value

    @field_validator('csrf_secret', 'abuse_hmac_secret')
    @classmethod
    def strong_secret(cls, value: str) -> str:
        if len(value) < 32 or value.lower().startswith(('replace', 'change')):
            raise ValueError('Set a distinct random secret of at least 32 characters')
        return value

    @field_validator('public_origin')
    @classmethod
    def origin(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.path not in ('', '/') or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('PUBLIC_ORIGIN must be an exact http/https origin')
        return value.rstrip('/')

    @model_validator(mode='after')
    def secure_production(self):
        if self.csrf_secret == self.abuse_hmac_secret:
            raise ValueError('CSRF and abuse secrets must differ')
        if self.app_env == 'production' and not self.public_origin.startswith('https://'):
            raise ValueError('Production requires HTTPS and secure cookies')
        if min(self.session_absolute_seconds, self.session_idle_seconds, self.contact_retention_days, self.contact_ip_limit, self.contact_site_limit) < 1:
            raise ValueError('Durations and limits must be positive')
        return self

    @property
    def cookie_name(self) -> str:
        return '__Host-portfolio_session' if self.app_env == 'production' else 'portfolio_dev_session'


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # Required values are supplied by BaseSettings environment loading.
