import streamlit as st
from src.agents.conversational_agent import ConversationalAgent
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the ConversationalAgent
@st.cache_resource
def get_conversational_agent():
    try:
        agent = ConversationalAgent()
        return agent
    except ValueError as e:
        st.error(f"Configuration Error: {e}. Please check your .env file.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred during agent initialization: {e}")
        st.stop()

conversational_agent = get_conversational_agent()

st.title("Assistente de Pesquisa Acadêmica")
st.markdown("Faça perguntas sobre seus documentos acadêmicos indexados.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Sua pergunta..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Buscando e gerando resposta..."):
            try:
                response = conversational_agent.run(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Erro ao gerar resposta: {e}")
                logging.error(f"Error generating response for prompt '{prompt}': {e}")
