import json
import time
import re
import uuid
import streamlit as st
from scipy.io import wavfile
import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import ExtractiveSummaryAction, AbstractiveSummaryAction
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import openai


st.set_page_config(layout="wide")

@st.cache_data
def create_transcription_request(audio_file, speech_recognition_language="en-US"):
    """Transcribe the contents of an audio file. Key assumptions:
    - The audio file is in WAV format.
    - The audio file is mono.
    - The audio file has a sample rate of 16 kHz.
    - Speech key and region are stored in Streamlit secrets."""

    speech_key = st.secrets["speech"]["key"]
    speech_region = st.secrets["speech"]["region"]

    # Create an instance of a speech config with specified subscription key and service region.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language=speech_recognition_language

    # Prepare audio settings for the wave stream
    channels = 1
    bits_per_sample = 16
    samples_per_second = 16000

    # Create audio configuration using the push stream
    wave_format = speechsdk.audio.AudioStreamFormat(samples_per_second, bits_per_sample, channels)
    stream = speechsdk.audio.PushAudioInputStream(stream_format=wave_format)
    audio_config = speechsdk.audio.AudioConfig(stream=stream)

    transcriber = speechsdk.transcription.ConversationTranscriber(speech_config, audio_config)
    all_results = []

    def handle_final_result(evt):
        all_results.append(evt.result.text)

    done = False

    def stop_cb(evt):
        print(f'CLOSING on {evt}')
        nonlocal done
        done= True

    # TODO: Subscribe to the events fired by the conversation transcriber
    # TODO: stop continuous transcription on either session stopped or canceled events

    # TODO: remove this placeholder code and perform the actual transcription
    all_results = ['This is a test.', 'Fill in with real transcription.']

    return all_results

def make_azure_openai_chat_request(system, call_contents):
    """Create and return a new chat completion request. Key assumptions:
    - Azure OpenAI endpoint, key, and deployment name stored in Streamlit secrets."""

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
            {"role": "system", "content": system},
            {"role": "user", "content": call_contents}
        ],
    )

@st.cache_data
def is_call_in_compliance(call_contents, include_recording_message, is_relevant_to_topic):
    """Analyze a call for relevance and compliance."""

    return "This is a placeholder result. Fill in with real compliance analysis."

@st.cache_data
def generate_extractive_summary(call_contents):
    """Generate an extractive summary of a call transcript. Key assumptions:
    - Azure AI Services Language service endpoint and key stored in Streamlit secrets."""

    language_endpoint = st.secrets["language"]["endpoint"]
    language_key = st.secrets["language"]["key"]

    # The call_contents parameter is formatted as a list of strings.
    # Join them together with spaces to pass in as a single document.
    joined_call_contents = ' '.join(call_contents)

    return "This is a placeholder result. Fill in with real extractive summary."

@st.cache_data
def generate_abstractive_summary(call_contents):
    """Generate an abstractive summary of a call transcript. Key assumptions:
    - Azure AI Services Language service endpoint and key stored in Streamlit secrets."""

    language_endpoint = st.secrets["language"]["endpoint"]
    language_key = st.secrets["language"]["key"]

    # The call_contents parameter is formatted as a list of strings.
    # Join them together with spaces to pass in as a single document.
    joined_call_contents = ' '.join(call_contents)

    return "This is a placeholder result. Fill in with real abstractive summary."

@st.cache_data
def generate_query_based_summary(call_contents):
    """Generate a query-based summary of a call transcript."""

    # The call_contents parameter is formatted as a list of strings.
    # Join them together with spaces to pass in as a single document.
    joined_call_contents = ' '.join(call_contents)

    return "This is a placeholder result. Fill in with real query-based summary."

@st.cache_data
def create_sentiment_analysis_and_opinion_mining_request(call_contents):
    """Analyze the sentiment of a call transcript and mine opinions. Key assumptions:
    - Azure AI Services Language service endpoint and key stored in Streamlit secrets."""

    language_endpoint = st.secrets["language"]["endpoint"]
    language_key = st.secrets["language"]["key"]

    # The call_contents parameter is formatted as a list of strings.
    # Join them together with spaces to pass in as a single document.
    joined_call_contents = ' '.join(call_contents)

    return "This is a placeholder result. Fill in with real sentiment analysis."

def make_azure_openai_embedding_request(text):
    """Create and return a new embedding request. Key assumptions:
    - Azure OpenAI endpoint, key, and deployment name stored in Streamlit secrets."""

    return "This is a placeholder result. Fill in with real embedding."

def normalize_text(s):
    """Normalize text for tokenization."""

    s = re.sub(r'\s+',  ' ', s).strip()
    s = re.sub(r". ,","",s)
    # remove all instances of multiple spaces
    s = s.replace("..",".")
    s = s.replace(". .",".")
    s = s.replace("\n", "")
    s = s.strip()

    return s

def generate_embeddings_for_call_contents(call_contents):
    """Generate embeddings for call contents. Key assumptions:
    - Call contents is a single string.
    - Azure OpenAI endpoint, key, and deployment name stored in Streamlit secrets."""

    # Normalize the text for tokenization
    # Call make_azure_openai_embedding_request() with the normalized content
    # Return the embeddings

    return [0, 0, 0]

def save_transcript_to_cosmos_db(transcript_item):
    """Save embeddings to Cosmos DB vector store. Key assumptions:
    - transcript_item is a JSON object containing call_id (int), 
        call_transcript (string), and request_vector (list).
    - Cosmos DB endpoint, client_id, and database name stored in Streamlit secrets."""

    cosmos_client_id = st.secrets["cosmos"]["client_id"]
    cosmos_credentials = DefaultAzureCredential(managed_identity_client_id=cosmos_client_id)

    cosmos_endpoint = st.secrets["cosmos"]["endpoint"]
    cosmos_database_name = st.secrets["cosmos"]["database_name"]
    cosmos_container_name = "CallTranscripts"

    # Create a CosmosClient
    # Load the Cosmos database and container
    # Insert the call transcript

####################### HELPER FUNCTIONS FOR MAIN() #######################
def perform_audio_transcription(uploaded_file):
    """Generate a transcription of an uploaded audio file."""

    st.audio(uploaded_file, format='audio/wav')
    with st.spinner("Transcribing the call..."):
        all_results = create_transcription_request(uploaded_file)
        return all_results

def perform_compliance_check(call_contents, include_recording_message, is_relevant_to_topic):
    """Perform a compliance check on a call transcript."""

    with st.spinner("Checking for compliance..."):
        if 'file_transcription_results' in st.session_state:
            call_contents = st.session_state.file_transcription_results
            if call_contents is not None and len(call_contents) > 0:
                st.session_state.compliance_results = is_call_in_compliance(
                    call_contents, include_recording_message, is_relevant_to_topic)
            st.success("Compliance check complete!")
        else:
            st.write("Please upload an audio file before checking for compliance.")

def perform_extractive_summary_generation():
    """Generate an extractive summary of a call transcript.
    That is, a summary that extracts key sentences from the call transcript."""

    # Set call_contents to file_transcription_results.
    # If it is empty, write out an error message for the user.
    if 'file_transcription_results' in st.session_state:
        # Use st.spinner() to wrap the summarization process.
        with st.spinner("Generating extractive summary..."):
            if 'extractive_summary' in st.session_state:
                extractive_summary = st.session_state.extractive_summary
            else:
                # Call the generate_extractive_summary function and set
                # its results to a variable named extractive_summary.
                ftr = st.session_state.file_transcription_results
                extractive_summary = generate_extractive_summary(ftr)
                # Save the extractive_summary value to session state.
                st.session_state.extractive_summary = extractive_summary

            # Call st.success() to indicate that the extractive summarization process is complete.
            if extractive_summary is not None:
                st.success("Extractive summarization complete!")
    else:
        st.error("Please upload an audio file before attempting to generate a summary.")

def perform_abstractive_summary_generation():
    """Generate an abstractive summary of a call transcript.
    That is, a summary that generates new sentences to summarize the call transcript."""

    # Set call_contents to file_transcription_results.
    # If it is empty, write out an error message for the user.
    if 'file_transcription_results' in st.session_state:
        # Use st.spinner() to wrap the summarization process.
        with st.spinner("Generating abstractive summary..."):
            # Call the generate_abstractive_summary function and set
            # its results to a variable named abstractive_summary.
            ftr = st.session_state.file_transcription_results
            abstractive_summary = generate_abstractive_summary(ftr)
            # Save the abstractive_summary value to session state.
            st.session_state.abstractive_summary = abstractive_summary

            # Call st.success() to indicate that the extractive summarization process is complete.
            if abstractive_summary is not None:
                st.success("Abstractive summarization complete!")
    else:
        st.error("Please upload an audio file before attempting to generate a summary.")

def perform_openai_summary():
    """Generate a query-based summary of a call transcript."""

    # Set call_contents to file_transcription_results.
    # If it is empty, write out an error message for the user.
    if 'file_transcription_results' in st.session_state:
        # Use st.spinner() to wrap the summarization process.
        with st.spinner("Generating Azure OpenAI summary..."):
            # Call the generate_query_based_summary function and set
            # its results to a variable named openai_summary.
            summary = generate_query_based_summary(st.session_state.file_transcription_results)
            # Save the openai_summary value to session state.
            st.session_state.openai_summary = summary

            if summary is not None:
                st.success("Azure OpenAI query-based summarization complete!")
    else:
        st.error("Please upload an audio file before attempting to generate a summary.")

def perform_sentiment_analysis_and_opinion_mining():
    """Analyze the sentiment of a call transcript and mine opinions."""

    # Set call_contents to file_transcription_results.
    # If it is empty, write out an error message for the user.
    if 'file_transcription_results' in st.session_state:
        # Use st.spinner() to wrap the sentiment analysis process.
        with st.spinner("Analyzing transcript sentiment and mining opinions..."):
            # Call the create_sentiment_analysis_and_opinion_mining_request
            # function and set its results to a variable named sentiment_and_mined_opinions.
            ftr = st.session_state.file_transcription_results
            smo = create_sentiment_analysis_and_opinion_mining_request(ftr)
            # Save the sentiment_and_mined_opinions value to session state.
            st.session_state.sentiment_and_mined_opinions = smo

            # Call st.success() to indicate that the sentiment analysis process is complete.
            if smo is not None:
                st.success("Sentiment analysis and opinion mining complete!")
    else:
        st.error("Please upload an audio file before attempting to analyze sentiment.")

def perform_save_embeddings_to_cosmos_db():
    """Save embeddings to Cosmos DB vector store."""

    # Set call_contents to file_transcription_results.
    # If it is empty, write out an error message for the user.
    if 'file_transcription_results' in st.session_state:
        # Use st.spinner() to wrap the embeddings saving process.
        with st.spinner("Saving embeddings to Cosmos DB..."):
            ftr = ' '.join(st.session_state.file_transcription_results)
            # Generate a call ID based on the text.
            # This is for demonstration purposes--a real system should use a unique ID.
            call_id = abs(hash(ftr)) % (10 ** 8)
            embeddings = generate_embeddings_for_call_contents(ftr)
            transcript_item = {
                "id": f'{call_id}_{uuid.uuid4()}',
                "call_id": call_id,
                "call_transcript": ftr,
                "request_vector": embeddings
            }
            save_transcript_to_cosmos_db(transcript_item)
            st.session_state.embedding_status = "Transcript and embeddings saved for this audio."
            st.success("Embeddings saved to Cosmos DB!")
    else:
        st.error("Please upload an audio file before attempting to save embeddings.")

def main():
    """Main function for the call center dashboard."""

    call_contents = []
    st.write(
    """
    # Call Center

    This Streamlit dashboard is intended to replicate some of the functionality
    of a call center monitoring solution. It is not intended to be a
    production-ready application.
    """
    )

    st.write("## Upload a Call")

    uploaded_file = st.file_uploader("Upload an audio file", type="wav")
    if uploaded_file is not None and ('file_transcription_results' not in st.session_state):
        st.session_state.file_transcription_results = perform_audio_transcription(uploaded_file)
        st.success("Transcription complete!")

    if 'file_transcription_results' in st.session_state:
        st.write(st.session_state.file_transcription_results)

    st.write("## Transcription Operations")

    comp, esum, asum, osum, sent, db = st.tabs(["Compliance",
        "Extractive Summary", "Abstractive Summary", "Azure OpenAI Summary",
        "Sentiment and Opinions", "Save to DB"])

    with comp:
        st.write("## Is Your Call in Compliance?")

        include_recording_message = st.checkbox("Call needs an indicator we are recording it")
        is_relevant_to_topic = st.checkbox("Call is relevant to the hotel and resort industry")

        if st.button("Check for Compliance"):
            perform_compliance_check(call_contents, include_recording_message, is_relevant_to_topic)

        # Write the call_contents value to the Streamlit dashboard.
        if 'compliance_results' in st.session_state:
            st.write(st.session_state.compliance_results)
    with esum:
        if st.button("Generate extractive summary"):
            perform_extractive_summary_generation()

        # Write the extractive_summary value to the Streamlit dashboard.
        if 'extractive_summary' in st.session_state:
            st.write(st.session_state.extractive_summary)
    with asum:
        if st.button("Generate abstractive summary"):
            perform_abstractive_summary_generation()

        # Write the abstractive_summary value to the Streamlit dashboard.
        if 'abstractive_summary' in st.session_state:
            st.write(st.session_state.abstractive_summary)
    with osum:
        if st.button("Generate query-based summary"):
            perform_openai_summary()

        # Write the openai_summary value to the Streamlit dashboard.
        if 'openai_summary' in st.session_state:
            st.write(st.session_state.openai_summary)
    with sent:
        if st.button("Analyze sentiment and mine opinions"):
            perform_sentiment_analysis_and_opinion_mining()

        # Write the sentiment_and_mined_opinions value to the Streamlit dashboard.
        if 'sentiment_and_mined_opinions' in st.session_state:
            st.write(st.session_state.sentiment_and_mined_opinions)
    with db:
        if st.button("Save embeddings to Cosmos DB"):
            perform_save_embeddings_to_cosmos_db()

        # Write the embedding_status value to the Streamlit dashboard.
        if 'embedding_status' in st.session_state:
            st.write(st.session_state.embedding_status)

if __name__ == "__main__":
    main()
