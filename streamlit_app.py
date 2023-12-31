import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader
from llama_index import GPTVectorStoreIndex, download_loader

st.set_page_config(page_title="KeyBot, the virtual assistant of KeyMind", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
# st.title("LegalBot, el asistente virtual de Contexto Legal, estoy para ayudarte! 💬")
# st.info("Revisa toda la información de Contexto en nuestra [página web](https://www.contextolegal.mx)", icon="📃")
         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, my name is KeyBot, ask me anything about the services and information of KeyMind Consulting."}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading! This can take up to 1 min."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        # service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert on the Streamlit Python library and your job is to answer technical questions. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features."))
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", 
                                                                  temperature=0.7, 
                                                                  system_prompt="You are a virtual assistant named KeyBot. You are an expert in the services of KeyMind Consulting and your work is to answer any question regarding the services and information about the company. Keep your answers technical and based on facts – do not hallucinate features.")) 
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        
        
        # SimpleWebPageReader = download_loader("SimpleWebPageReader", custom_path="local_dir")

        # loader = SimpleWebPageReader()
        # documents = loader.load_data(urls=['https://www.contextolegal.mx/', 'https://www.contextolegal.mx/faq'])
        # index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)
        return index





index = load_data()

from llama_index.memory import ChatMemoryBuffer

memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
# chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True, system_prompt="You are an expert on the Streamlit Python library and your job is to answer technical questions. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features.")
chat_engine = index.as_chat_engine(chat_mode="context", memory=memory, verbose=True)

if prompt := st.chat_input("Ask me something"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
