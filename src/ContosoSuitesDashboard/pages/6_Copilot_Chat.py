import requests
import streamlit as st

st.set_page_config(layout="wide")

def send_message_to_copilot(message):
    """Send a message to the Copilot chat endpoint."""
    api_endpoint = st.secrets["api"]["endpoint"]
    # Exercise 5 Task 2 TODO #11: Send a POST request to the Copilot chat endpoint with the user message and assign the return value to response.
    response = ""
    return response.text

def main():
    """Main function for the Maintenance Copilot Chat Streamlit page."""

    st.write(
        """
        # Maintenance Copilot chat

        This Streamlit dashboard is intended to demonstrate how you can use
        a Semantic Kernel agent to generate and save a maintenance request.

        ## Ask the Copilot to generate a maintenance request
        """
    )

    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("How I can help you today?"):
        with st.spinner("Awaiting the Copilot's response to your question..."):
            # Exercise 5 Task 2 TODO #10: Set up a conversational chat interface with the Copilot using the steps below.
            pass # Remove this once you have defined the conversational chat interface

            # Display user message in chat message container

            # Add user message to chat history

            # Send user message to Copilot and get response

            # Display assistant response in chat message container

            # Add assistant response to chat history

if __name__ == "__main__":
    main()        
