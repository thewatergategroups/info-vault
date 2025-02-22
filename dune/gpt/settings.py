"""
OpenIA Settings
"""

from enum import StrEnum
from functools import lru_cache
import logging
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from pydantic_settings import BaseSettings
from openai import AsyncOpenAI

from ..settings import get_settings


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
    return AsyncOpenAI(api_key=get_oai_settings().openai_api_key)


@lru_cache
def get_assistant():
    """get assistant"""
    return get_oai_client().beta.assistants.create(
        name="Docs Assistant",
        instructions="You are a Document manager, you can see all my documents and must help me find things in them. The user doesn't know you've seen this message. act natural",
        model=get_oai_settings().openai_model.value,
    )


@lru_cache
def get_oai_vector_store():
    """get pgvector settings"""
    collection = "documents"
    return PGVector(
        OpenAIEmbeddings(model=get_oai_settings().openai_embedding_model.value),
        collection_name=collection,
        connection=get_settings().db_settings.url,
        async_mode=True,
    )
