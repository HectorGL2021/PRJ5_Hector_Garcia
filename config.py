"""Configuración de la aplicación Flask."""

import os


class Config:
    """Configuración base de la aplicación."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Construcción de la URI de PostgreSQL desde variables de entorno
    DB_USER = os.environ.get("DB_USER", "appuser")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "apppassword123")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    DB_NAME = os.environ.get("DB_NAME", "appdb")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    """Configuración para tests (SQLite en memoria)."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
