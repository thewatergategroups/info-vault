"""
OpenIA Settings
"""

from enum import StrEnum
from functools import lru_cache
import logging
from pydantic_settings import BaseSettings
from openai import OpenAI


class OaiModel(StrEnum):
    """
    Enum for OAI models
    """

    GPT4 = "gpt-4"
    GPT4o = "gpt-4o"


class OaiSettings(BaseSettings):
    """OpenAI Storage Settings"""

    openai_api_key: str = ""
    openai_model: OaiModel = OaiModel.GPT4


@lru_cache
def get_oai_settings():
    """Get OpenAI client"""
    return OaiSettings()


@lru_cache
def get_oai_client():
    """Get OpenAI client"""
    logging.info("settings %s", get_oai_settings())
    return OpenAI(api_key=get_oai_settings().openai_api_key)


@lru_cache
def get_assistant():
    """get assistant"""
    return get_oai_client().beta.assistants.create(
        name="Docs Assistant",
        instructions="You are a Document manager, you can see all my documents and must help me find things in them. The user doesn't know you've seen this message. act natural",
        model=get_oai_settings().openai_model.value,
    )
