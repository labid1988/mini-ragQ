# from pydantic_settings import BaseSettings, SettingsConfigDict

# class Settings(BaseSettings):
#     APP_NAME: str
#     APP_VERSION: str
#     OPENAI_API_KEY:str

#     FILE_ALLOWED_TYPES: str
#     FILE_MAX_SIZE: int

#     class Config:
#         env_file = ".env"
    
# def get_settings():
#     return Settings()

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str

    FILE_ALLOWED_TYPES: str = "application/pdf,text/plain"
    FILE_MAX_SIZE: int = 10
    FILE_DEFAULT_CHUNK_SIZE: int

    MONGODB_URL: str
    MONGODB_DATABASE: str
    
    @property
    def allowed_types(self):  # ← cette property doit être présente
        return [t.strip() for t in self.FILE_ALLOWED_TYPES.split(",")]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()