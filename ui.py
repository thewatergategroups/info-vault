"""
Doc UI with streamlit
"""

from functools import lru_cache
import re
import streamlit as st
import httpx
from pydantic_settings import BaseSettings


class UiSettings(BaseSettings):
    """UI settings"""

    api_url: str = "http://localhost:8000"


@lru_cache
def get_ui_settings():
    """UI settings"""
    return UiSettings()


def ollama_chat():
    """
    Basic Page
    This reruns after every action
    """
    st.title("Welcome to OpenDoc")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can i help you?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.expander("Show thought process"):
                with httpx.stream(  # pylint: disable=not-context-manager
                    "POST",
                    f"{get_ui_settings().api_url}/ollama/stream",
                    json={"message": prompt},
                ) as response:
                    resp = st.write_stream(response.iter_text())
            cleaned = re.sub(r"<think>.*?</think>", "", resp, flags=re.DOTALL)
            st.markdown(cleaned)
        st.session_state.messages.append({"role": "assistant", "content": cleaned})


if __name__ == "__main__":
    ollama_chat()
