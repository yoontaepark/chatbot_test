# base libraries
import os
import streamlit as st
# lanchain function libraries
from langchain_core.messages import ChatMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import BaseChatMessageHistory 
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
# model libraries
from langchain_mistralai import ChatMistralAI
# from langchain_openai import ChatOpenAI

# custom libraries
from utils import print_messages, StreamHandler

################################################################################
###########################   MAIN CODE   ######################################
################################################################################
# setup mistral api key, load model
os.environ["MISTRAL_API_KEY"] = st.secrets["MISTRAL_API_KEY"]

# 1) Title
st.set_page_config(page_title="ChatGPT", page_icon="🦜️")
st.title("🦜️ChatGPT") 

# 2) cacheing the chat messages
# initialize 
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# add storage init statement 
if "store" not in st.session_state:
    st.session_state["store"] = {}

# Sidebar
with st.sidebar:
    session_id = st.text_input("Session ID", value="abc123")
    
    # clear button 
    clear_btn = st.button("Clear current conversation")
    if clear_btn:
        st.session_state["messages"] = []
        st.session_state["store"] = {}
        st.rerun() # refresh the chat 

# print all cached messages: So this will make chat scrollable
print_messages()


# session storage(history) function
def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    """Get the session history from the session storage."""
    if session_ids not in st.session_state["store"]:
        # create a new chat message history
        st.session_state["store"][session_ids] = ChatMessageHistory()
    return st.session_state["store"][session_ids] # return session_id info 

# 3) Chat input:  
if user_input:= st.chat_input("Say something"): # if user inputs
    # user input
    st.chat_message("user").write(f"{user_input}") # it writes on the chat board
    st.session_state["messages"].append(ChatMessage(role="user", content=user_input)) # appends the user input to the cache
    
   
    # AI output response
    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty()) # markdown each token in chat 
        
        # 1) load model
        llm = ChatMistralAI(model="mistral-large-latest", streaming=True, callbacks=[stream_handler])
        
        # 2) generate prompt
        prompt = ChatPromptTemplate.from_messages(
            [   
                # system
                (
                    "system",
                    "Answer the following questions short and concisely."
                ),
                
                # store message 
                MessagesPlaceholder(variable_name="history"),
                
                # user input
                ("human", "{question}"),
            ]
            )
        
        # 3) Create chain 
        chain = prompt | llm 
        # chain = prompt | model | StrOutputParser() # StrOutputParser is used to parse the response as a string
        
        # 4) save conversation history
        chain_with_memory = (
            RunnableWithMessageHistory(
                chain, # chain 
                get_session_history, # get session history function
                input_messages_key="question", # input messages key
                history_messages_key="history",        
            )
        )
        
        # 5) invoke chain 
        response = chain_with_memory.invoke(
            {"question": user_input}, 
            config={"configurable": {"session_id": session_id}},
        )
        
        msg = response.content
        
        # st.write(msg) # if you want to print response. For now removed as we are using stream_handler
        st.session_state["messages"].append(ChatMessage(role="assistant", content=msg))     
