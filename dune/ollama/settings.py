"""
Ollama Settings
https://ollama.com/blog/embedding-models
"""

from enum import StrEnum
from functools import lru_cache
import logging
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_postgres import PGVector
from pydantic_settings import BaseSettings

from ..settings import get_settings


class OllamaModel(StrEnum):
    """
    Enum for Ollama models
    """

    DEEPSEEK_R114B = "deepseek-r1:14b"
    DEEPSEEK_R18B = "deepseek-r1:8b"


class OllamaEmbeddingModel(StrEnum):
    """
    Enum for Ollama models
    """

    NOMIC_EMBED_MODEL = "nomic-embed-text"
    MXBAI_EMBED_LARGE = "mxbai-embed-large"
    ALL_MINILM = "all-minilm"


class OllamaSettings(BaseSettings):
    """OpenAI Storage Settings"""

    ollama_model: OllamaModel = OllamaModel.DEEPSEEK_R18B
    ollama_embeddings_model: OllamaEmbeddingModel = (
        OllamaEmbeddingModel.NOMIC_EMBED_MODEL
    )
    ollama_url: str = "http://localhost:11434"


@lru_cache
def get_ollama_settings():
    """Get Ollama client"""
    return OllamaSettings()


@lru_cache
def get_ollama_client():
    """Get OpenAI client"""
    settings = get_ollama_settings()
    logging.info("settings %s", settings)
    return ChatOllama(model=settings.ollama_model, base_url=settings.ollama_url)


@lru_cache
def get_ollama_vector_store():
    """get pgvector settings"""
    collection = "documents"
    return PGVector(
        OllamaEmbeddings(
            model=get_ollama_settings().ollama_model.value,
            base_url=get_ollama_settings().ollama_url,
        ),
        collection_name=collection,
        connection=get_settings().db_settings.url,
        async_mode=True,
    )
