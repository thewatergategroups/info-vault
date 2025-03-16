"""
OpenIA Settings
"""

from enum import StrEnum
from functools import lru_cache
import logging
from pydantic_settings import BaseSettings
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI


class OaiModel(StrEnum):
    """
    Enum for OAI models
    """

    GPT4 = "gpt-4"
    GPT4o = "gpt-4o"


class OaiEmbeddingModel(StrEnum):
    """embeddings models"""

    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"


class OaiSettings(BaseSettings):
    """OpenAI Storage Settings"""

    openai_api_key: str = ""
    openai_model: OaiModel = OaiModel.GPT4
    openai_embedding_model: OaiEmbeddingModel = OaiEmbeddingModel.TEXT_EMBEDDING_3_LARGE


@lru_cache
def get_oai_settings():
    """Get OpenAI client"""
    return OaiSettings()


@lru_cache
def get_oai_client():
    """Get OpenAI client"""
    logging.info("settings %s", get_oai_settings())
    return ChatOpenAI(
        model=get_oai_settings().openai_model.value,
        api_key=get_oai_settings().openai_model.value,
        timeout=20,
        max_retries=2,
        temperature=0.7,
    )
