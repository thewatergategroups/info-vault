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

    oai_key: str = ""
    oai_model: OaiModel = OaiModel.GPT4


@lru_cache
def get_oai_settings():
    """Get OpenAI client"""
    return OaiSettings()


@lru_cache
def get_oai_client():
    """Get OpenAI client"""
    logging.info("settings %s", get_oai_settings())
    return OpenAI(api_key=get_oai_settings().oai_key)


@lru_cache
def get_assistant():
    """get assistant"""
    return get_oai_client().beta.assistants.create(
        name="Docs Assistant",
        instructions="You are a Document manager, you can see all my documents and must help me find things in them.",
        model=get_oai_settings().oai_model.value,
    )


def create_thread():
    """create oai thread"""
    return get_oai_client().beta.threads.create()


def delete_thread(thread_id: str):
    """create oai thread"""
    return get_oai_client().beta.threads.delete(thread_id)


def retrieve_thread(thread_id: str):
    """create oai thread"""
    return get_oai_client().beta.threads.retrieve(thread_id)


def add_message(thread_id: str, message: str):
    """Add message to thread"""
    return get_oai_client().beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message,
    )


def get_messages(thread_id: str):
    return get_oai_client().beta.threads.messages.list(thread_id=thread_id)
