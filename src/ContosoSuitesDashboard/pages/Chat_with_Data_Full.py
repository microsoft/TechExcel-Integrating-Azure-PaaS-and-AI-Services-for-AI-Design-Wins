import streamlit as st
import requests
import pandas as pd
import json
import openai
import inspect
import azure.cognitiveservices.speech as speechsdk

st.set_page_config(layout="wide")

with open('config_full.json') as f:
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
    client = openai.AzureOpenAI(
        base_url=f"{aoai_endpoint}/openai/deployments/{deployment_name}/extensions/",
        api_key=aoai_api_key,
        api_version="2023-12-01-preview"
    )
    # Create and return a new chat completion request
    # Be sure to include the "extra_body" parameter to use Azure AI Search as the data source
    return client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ],
        stream=True,
        extra_body={
            "dataSources": [
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": endpoint,
                        "key": key,
                        "indexName": index_name,
                    }
                }
            ]
        }
    )

def handle_chat_prompt(prompt):
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
        for response in create_chat_completion(deployment_name, st.session_state.messages, config["SearchEndpoint"], config["SearchKey"], config["SearchIndex"]):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

### Exercise 03: Function calls
def get_customers(search_criterion, search_value):
    full_server_url = f"http://localhost:5292/Customer/?searchCriterion={search_criterion}&searchValue={search_value}"
    r = requests.get(
        full_server_url,
        headers={"Content-Type": "application/json"}
    )
    if r.status_code == 200:
        return st.write(pd.read_json(r.content.decode("utf-8")))
    else:
        return f"Failure to find any customers with {search_criterion} {search_value}."

functions = [
    {
        "name": "get_customers",
        "description": "Get a list of customers based on some search criterion.",
        "parameters": {
            "type": "object",
            "properties": {
                "search_criterion": {"type": "string", "enum": ["CustomerName", "LoyaltyTier", "DateOfMostRecentStay"]},
                "search_value": {"type": "string"},
            },
            "required": ["search_criterion", "search_value"],
        },
    }
]

available_functions = {
    "get_customers": get_customers,
}

def create_chat_completion_with_functions(deployment_name, messages):
    # Create an Azure OpenAI client. We create it in here because each exercise will
    # require at a minimum different base URLs.
    client = openai.AzureOpenAI(
        base_url=f"{aoai_endpoint}/openai/deployments/{deployment_name}/",
        api_key=aoai_api_key,
        api_version="2023-12-01-preview"
    )
    # Create and return a new chat completion request
    # Be sure to include the "functions" parameter and set "function_call"
    return client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ],
        functions=functions,
        function_call="auto",
    )

def handle_chat_prompt_with_functions(prompt):
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
        response = create_chat_completion_with_functions(deployment_name, st.session_state.messages)
        response_message = response.choices[0].message

        # Check if GPT returned a function call
        if response_message.function_call:
            # Get the function name and arguments
            function_name = response_message.function_call.name
            # Verify the function
            if function_name not in available_functions:
                full_response = f"Sorry, I don't know how to call the function `{function_name}`."
            else:
                function_to_call = available_functions[function_name]
                # Verify the function has the correct number of arguments
                function_args = json.loads(response_message.function_call.arguments)
                if check_args(function_to_call, function_args) is False:
                    full_response = f"Sorry, I don't know how to call the function `{function_name}` with those arguments."
                else:
                    # Call the function
                    full_response = function_to_call(**function_args)
    message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

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
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language=speech_recognition_language

    # Create a microphone instance and speech recognizer.
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # Start speech recognition
    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    # Check the result
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        return None
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
        return None
    
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

    # Await a speech to text request
    # Note that Streamlit does not have a great interface for keeping chat in a specific location
    # so using this button will cause it to be in an awkward position after the first message.
    if st.button("Speech to text"):
        speech_contents = recognize_from_microphone(speech_key, speech_region)
        if speech_contents:
            handle_prompt(chat_option, speech_contents)

    # Await a user message and handle the chat prompt when it comes in.
    if prompt := st.chat_input("Enter a message:"):
        handle_prompt(chat_option, prompt)

if __name__ == "__main__":
    main()
