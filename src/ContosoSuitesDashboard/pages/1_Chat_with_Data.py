import streamlit as st
import openai

st.set_page_config(layout="wide")

def create_chat_completion(aoai_deployment_name, messages, aoai_endpoint, aoai_key):
    client = openai.AzureOpenAI(
        api_key=aoai_key,
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

def handle_chat_prompt(prompt, aoai_deployment_name, aoai_endpoint, aoai_key):
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
        for response in create_chat_completion(aoai_deployment_name, st.session_state.messages, aoai_endpoint, aoai_key):
            if response.choices:
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

def main():
    st.write(
    """
    # Chat with Data

    This Streamlit dashboard is intended to show off capabilities of Azure OpenAI, including integration with AI Search.
    """
    )

    aoai_endpoint = st.secrets["aoai"]["endpoint"]
    aoai_key = st.secrets["aoai"]["key"]
    aoai_deployment_name = st.secrets["aoai"]["deployment_name"]

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Await a user message and handle the chat prompt when it comes in.
    if prompt := st.chat_input("Enter a message:"):
        handle_chat_prompt(prompt, aoai_deployment_name, aoai_endpoint, aoai_key)

if __name__ == "__main__":
    main()
