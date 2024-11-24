from langchain_core.callbacks.base import BaseCallbackHandler
import streamlit as st

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token # add token to text
        self.container.markdown(self.text) # print(or markdown) the text

def print_messages():
    # print all cached messages
    if "messages" in st.session_state and len(st.session_state["messages"]) > 0:
        for chat in st.session_state["messages"]:
            st.chat_message(chat.role).write(chat.content)