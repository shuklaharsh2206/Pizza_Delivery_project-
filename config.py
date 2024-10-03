from pydantic import BaseSettings

class Settings(BaseSettings):
    authjwt_secret_key: str = "15deed16737e69e239527d42f8e387d98654038ef97ce21429b3c91ab0dd4308"

    class Config:
        env_file = ".env"
