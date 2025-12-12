# config/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "NovaMind API"
    env: str = "dev"

    # CORS
    cors_origins: list[str] = Field(default=["*"])

    # MySQL creds (usa .env en raíz del repo o variables de entorno)
    mysql_user: str = "root"
    mysql_password: str = "Familia27!"
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3308
    mysql_db: str = "novamind"

    # IA models (puedes cambiarlos aquí)
    sentiment_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    emotion_model: str = "j-hartmann/emotion-english-distilroberta-base"
    zeroshot_model: str = "facebook/bart-large-mnli"
    emotion_model = "pysentimiento/emotion-es"
    emotion_model = "samrawal/emotion-es"
    zeroshot_model = "recognai/bert-base-spanish-wwm-cased-xnli"
    summarizer_model = "mrm8488/t5-base-finetuned-summarize-news"

    summarizer_model: str = "sshleifer/distilbart-cnn-12-6"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
