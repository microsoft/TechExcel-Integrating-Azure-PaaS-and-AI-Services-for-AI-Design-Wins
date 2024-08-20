import streamlit as st
import requests
import pandas as pd
import json
import openai
import inspect
import azure.cognitiveservices.speech as speechsdk

st.set_page_config(layout="wide")

with open('config.json') as f:
    config = json.load(f)

aoai_endpoint = config['AOAIEndpoint']
aoai_api_key = config['AOAIKey']
deployment_name = config['AOAIDeploymentName']
speech_key = config['SpeechKey']
speech_region = config['SpeechRegion']

### Exercise 02: Chat with customer data
def create_chat_completion(deployment_name, messages, endpoint, key, index_name):
    # Create an Azure OpenAI client. We create it in here because each exercise will
    # require at a minimum different base URLs.
    #
    #client = openai.AzureOpenAI(
    #    base_url=f"{aoai_endpoint}/openai/deployments/{deployment_name}/extensions/",
    #    TODO: fill in rest of parameters
    #)
    
    # Create and return a new chat completion request
    # Be sure to include the "extra_body" parameter to use Azure AI Search as the data source

    #return client.chat.completions.create(
    #    model=deployment_name,
    #    messages=[
    #        {"role": m["role"], "content": m["content"]}
    #        for m in messages
    #    ],
    #    stream=True,
    #    TODO: fill in rest of function call
    #)
    
    raise NotImplementedError

def handle_chat_prompt(prompt):
    # Echo the user's prompt to the chat window
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send the user's prompt to Azure OpenAI and display the response
    # The call to Azure OpenAI is handled in create_chat_completion()
    # This function loops through the responses and displays them as they come in.
    # It also appends the full response to the chat history.

    #with st.chat_message("assistant"):
    #    message_placeholder = st.empty()
    #    full_response = ""
    #    for response in ... TODO: finish call
    #st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    raise NotImplementedError

### Exercise 03: Function calls
def get_customers(search_criterion, search_value):
    # Set up the API request
    full_server_url = f"TODO: fill this in"
    r = requests.get(
        full_server_url,
        headers={"Content-Type": "application/json"}
    )
    if r.status_code == 200:
        return st.write(pd.read_json(r.content.decode("utf-8")))
    else:
        return f"Failure to find any customers with {search_criterion} {search_value}."

# TODO: fill in the function call definition
functions = [
]

available_functions = {
    "get_customers": get_customers,
}

def create_chat_completion_with_functions(deployment_name, messages):
    # Create an Azure OpenAI client. We create it in here because each exercise will
    # require at a minimum different base URLs.
    #
    #client = openai.AzureOpenAI(
    #    base_url=f"{aoai_endpoint}/openai/deployments/{deployment_name}/",
    #    TODO: fill in rest of parameters
    #)
    
    # Create and return a new chat completion request
    # Be sure to include the "functions" parameter and set "function_call"

    #return client.chat.completions.create(
    #    model=deployment_name,
    #    messages=[
    #        {"role": m["role"], "content": m["content"]}
    #        for m in messages
    #    ],
    #    TODO: fill in rest of function call
    #)
    
    raise NotImplementedError

def handle_chat_prompt_with_functions(prompt):
    # Echo the user's prompt to the chat window
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send the user's prompt to Azure OpenAI and display the response
    # The call to Azure OpenAI is handled in create_chat_completion()
    # This function loops through the responses and displays them as they come in.
    # It also appends the full response to the chat history.

    #with st.chat_message("assistant"):
    #    message_placeholder = st.empty()
    #    full_response = ""
    #    response = TODO: finish call and extract message as response_message
    #
    #    # Check if GPT returned a function call
    #    if response_message.function_call:
    #        # Get the function name and arguments
    #        TODO: fill in code
    #
    #        # Verify the function
    #        if function_name not in available_functions:
    #            full_response = f"Sorry, I don't know how to call the function `{function_name}`."
    #        else:
    #            function_to_call = available_functions[function_name]
    #            # Verify the function has the correct number of arguments
    #            function_args = json.loads(response_message.function_call.arguments)
    #            if check_args(function_to_call, function_args) is False:
    #                full_response = f"Sorry, I don't know how to call the function `{function_name}` with those arguments."
    #            else:
    #                # Call the function
    #                full_response = function_to_call(**function_args)
    #message_placeholder.markdown(full_response)
    #st.session_state.messages.append({"role": "assistant", "content": full_response})

    raise NotImplementedError

# helper method used to check if the correct arguments are provided to a function
def check_args(function, args):
    sig = inspect.signature(function)
    params = sig.parameters

    # Check if there are extra arguments
    for name in args:
        if name not in params:
            return False
    # Check if the required arguments are provided 
    for name, param in params.items():
        if param.default is param.empty and name not in args:
            return False

    return True


### Exercise 04
def recognize_from_microphone(speech_key, speech_region, speech_recognition_language="en-US"):
    # Create an instance of a speech config with specified subscription key and service region.
    # Then set the speech recognition language to speech_recognition_language.

    # TODO: fill in code
    # speech_config = ...

    # Create a microphone instance and speech recognizer.

    # TODO: fill in code
    # audio_config = ...
    # speech_recognizer = ...

    # Start speech recognition

    # print("Speak into your microphone.")
    # speech_recognition_result = speech_recognizer.recognize_once_async().get()

    # Check the result

    # if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
    #     print("Recognized: {}".format(speech_recognition_result.text))
    #     return ...
    # elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
    #     print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    #     return ...
    # elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
    #     cancellation_details = speech_recognition_result.cancellation_details
    #     print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    #     if cancellation_details.reason == speechsdk.CancellationReason.Error:
    #         print("Error details: {}".format(cancellation_details.error_details))
    #         print("Did you set the speech resource key and region values?")
    #     return ...
    
    raise NotImplementedError
    

### All Exercises
def handle_prompt(chat_option, prompt):
    if chat_option == "Chat with Data":
        handle_chat_prompt(prompt)
    elif chat_option == "Function Calls":
        handle_chat_prompt_with_functions(prompt)
    else:
        st.write("Please select a chat option before calling the chatbot.")

def main():
    st.write(
    """
    # Chat with Data

    This Streamlit dashboard is intended to show off capabilities of Azure OpenAI, including integration with AI Search, Azure Speech Services, and external APIs.
    """
    )

    chat_option = st.radio(label="Choose the chat option you want to try:", options=["Chat with Data", "Function Calls"])

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Exercise 04: Await a speech to text request
    # Note that Streamlit does not have a great interface for keeping chat in a specific location
    # so using this button will cause it to be in an awkward position after the first message.
    
    # TODO: complete this section
    # if st.button("Speech to text"):

    # Await a user message and handle the chat prompt when it comes in.
    if prompt := st.chat_input("Enter a message:"):
        handle_prompt(chat_option, prompt)

if __name__ == "__main__":
    main()
