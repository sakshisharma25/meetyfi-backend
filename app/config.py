from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import Field
from pathlib import Path

# Define a path
template_folder = Path("path/to/templates")

# Check if it's a directory
if template_folder.is_dir():
    print("It's a valid directory.")
else:
    print("Not a directory.")


class Settings(BaseSettings):
    PROJECT_NAME: str = "Meetyfi"
    MONGODB_URL: str 
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GOOGLE_MAPS_API_KEY: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    MAIL_STARTTLS: bool = Field(default=True)
    MAIL_SSL_TLS: bool = Field(default=False)
    TEMPLATE_FOLDER: Path = Field(
        default=Path("C:/Users/Sakshi Sharma/meetyfi-backend/app/core/email_templates")
    )
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()