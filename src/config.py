"""
Configuration management for the We Go Mars platform.

This module handles all application settings including LLM configuration,
Qdrant connection, and workflow parameters.

Owner: [ASSIGN TEAMMATE]
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    openai_api_key: str = ""
    llm_model: str = "gpt-4.1-mini"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096

    # Qdrant Vector Database
    qdrant_url: str = ""  # Cloud URL (takes precedence over host/port if set)
    qdrant_api_key: str = ""
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Workflow Configuration
    max_refinement_iterations: int = 5
    proposer_count: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
