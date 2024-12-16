import streamlit as st
import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

st.set_page_config(layout="wide")

def create_chat_completion(messages):
    """Create and return a new chat completion request. Key assumptions:
    - The Azure OpenAI endpoint and deployment name are stored in Streamlit secrets."""

    # Retrieve secrets from the Streamlit secret store.
    # This is a secure way to store sensitive information that you don't want to expose in your code.
    # Learn more about Streamlit secrets here: https://docs.streamlit.io/develop/concepts/connections/secrets-management
    # The secrets themselves are stored in the .streamlit/secrets.toml file.

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    
    aoai_endpoint = st.secrets["aoai"]["endpoint"]
    aoai_deployment_name = st.secrets["aoai"]["deployment_name"]

    client = openai.AzureOpenAI(
        azure_ad_token_provider=token_provider,
        api_version="2024-06-01",
        azure_endpoint = aoai_endpoint
    )
    # Create and return a new chat completion request
    return client.chat.completions.create(
        model=aoai_deployment_name,
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ],
        stream=True
    )

def handle_chat_prompt(prompt):
    """Echo the user's prompt to the chat window.
    Then, send the user's prompt to Azure OpenAI and display the response."""

    # Echo the user's prompt to the chat window
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
 
    # Send the user's prompt to Azure OpenAI and display the response
    # The call to Azure OpenAI is handled in create_chat_completion()
    # This function loops through the responses and displays them as they come in.
    # It also appends the full response to the chat history.
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in create_chat_completion(st.session_state.messages):
            if response.choices:
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

def main():
    """Main function for the Chat with Data Streamlit app."""

    st.write(
    """
    # Chat with Data

    This Streamlit dashboard is intended to show off capabilities of Azure OpenAI, including integration with AI Search.
    """
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Await a user message and handle the chat prompt when it comes in.
    if prompt := st.chat_input("Enter a message:"):
        handle_chat_prompt(prompt)

if __name__ == "__main__":
    main()
