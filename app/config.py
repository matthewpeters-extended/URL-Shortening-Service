from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Used to build the shortUrl returned from POST /shorten, e.g.
    # "http://127.0.0.1:8000/shorten/b".
    base_url: str = "http://127.0.0.1:8000"


settings = Settings()
