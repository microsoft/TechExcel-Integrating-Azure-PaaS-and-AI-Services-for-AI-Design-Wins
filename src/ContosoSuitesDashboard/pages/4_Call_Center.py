import json
import time
import re
import tiktoken
import streamlit as st
from scipy.io import wavfile
import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import ExtractiveSummaryAction, AbstractiveSummaryAction
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

    # Subscribe to the events fired by the conversation transcriber
    transcriber.transcribed.connect(handle_final_result)
    transcriber.session_started.connect(lambda evt: print(f'SESSION STARTED: {evt}'))
    transcriber.session_stopped.connect(lambda evt: print(f'SESSION STOPPED {evt}'))
    transcriber.canceled.connect(lambda evt: print(f'CANCELED {evt}'))
    # stop continuous transcription on either session stopped or canceled events
    transcriber.session_stopped.connect(stop_cb)
    transcriber.canceled.connect(stop_cb)

    transcriber.start_transcribing_async()

    # Read the whole wave files at once and stream it to sdk
    _, wav_data = wavfile.read(audio_file)
    stream.write(wav_data.tobytes())
    stream.close()
    while not done:
        time.sleep(.5)

    transcriber.stop_transcribing_async()
    return all_results

def make_azure_openai_chat_request(system, call_contents):
    """Create and return a new chat completion request. Key assumptions:
    - Azure OpenAI endpoint, key, and deployment name stored in Streamlit secrets."""

    aoai_endpoint = st.secrets["aoai"]["endpoint"]
    aoai_key = st.secrets["aoai"]["key"]
    aoai_deployment_name = st.secrets["aoai"]["deployment_name"]

    client = openai.AzureOpenAI(
        api_key=aoai_key,
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

    joined_call_contents = ' '.join(call_contents)
    if include_recording_message:
        include_recording_message_text = "2. Was the caller aware that the call was being recorded?"
    else:
        include_recording_message_text = ""

    if is_relevant_to_topic:
        is_relevant_to_topic_text = "3. Was the call relevant to the hotel and resort industry?"
    else:
        is_relevant_to_topic_text = ""

    system = f"""
        You are an automated analysis system for Contoso Suites.
        Contoso Suites is a luxury hotel and resort chain with locations
        in a variety of Caribbean nations and territories.
        
        You are analyzing a call for relevance and compliance.

        You will only answer the following questions based on the call contents:
        1. Was there vulgarity on the call?
        {include_recording_message_text}
        {is_relevant_to_topic_text}
    """

    response = make_azure_openai_chat_request(system, joined_call_contents)
    return response.choices[0].message.content

@st.cache_data
def generate_query_based_summary(call_contents):
    """Generate a query-based summary of a call transcript."""

    # The call_contents parameter is formatted as a list of strings.
    # Join them together with spaces to pass in as a single document.
    joined_call_contents = ' '.join(call_contents)

    # Write a system prompt that instructs the large language model to:
    #    - Generate a short (5 word) summary from the call transcript.
    #    - Create a two-sentence summary of the call transcript.
    #    - Output the response in JSON format, with the short summary
    #       labeled 'call-title' and the longer summary labeled 'call-summary.'
    system = """
        Write a five-word summary and label it as call-title.
        Write a two-sentence summary and label it as call-summary.

        Output the results in JSON format.
    """

    # Call make_azure_openai_chat_request().
    response = make_azure_openai_chat_request(system, joined_call_contents)

    # Return the summary.
    return response.choices[0].message.content

@st.cache_data
def generate_extractive_summary(call_contents):
    """Generate an extractive summary of a call transcript. Key assumptions:
    - Azure Text Analytics endpoint and key stored in Streamlit secrets."""

    language_endpoint = st.secrets["language"]["endpoint"]
    language_key = st.secrets["language"]["key"]

    # The call_contents parameter is formatted as a list of strings.
    # Join them together with spaces to pass in as a single document.
    joined_call_contents = ' '.join(call_contents)

    # Create a TextAnalyticsClient, connecting it to your Language Service endpoint.
    client = TextAnalyticsClient(language_endpoint, AzureKeyCredential(language_key))
    # Call the begin_analyze_actions method on your client, passing in the joined
    # call_contents as an array and an ExtractiveSummaryAction with a max_sentence_count of 2.
    poller = client.begin_analyze_actions(
        [joined_call_contents],
        actions = [
            ExtractiveSummaryAction(max_sentence_count=2)
        ]
    )

    # Extract the summary sentences and merge them into a single summary string.
    for result in poller.result():
        summary_result = result[0]
        if summary_result.is_error:
            st.error(f'Extractive summary resulted in an error with code "{summary_result.code}" and message "{summary_result.message}"')
            return ''

        extractive_summary = " ".join([sentence.text for sentence in summary_result.sentences])

    # Return the summary as a JSON object in the shape '{"call-summary": extractive_summary}'
    return json.loads('{"call-summary":"' + extractive_summary + '"}')

@st.cache_data
def generate_abstractive_summary(call_contents):
    """Generate an abstractive summary of a call transcript. Key assumptions:
    - Azure Text Analytics endpoint and key stored in Streamlit secrets."""

    language_endpoint = st.secrets["language"]["endpoint"]
    language_key = st.secrets["language"]["key"]

    # The call_contents parameter is formatted as a list of strings.
    # Join them together with spaces to pass in as a single document.
    joined_call_contents = ' '.join(call_contents)

    # Create a TextAnalyticsClient, connecting it to your Language Service endpoint.
    client = TextAnalyticsClient(language_endpoint, AzureKeyCredential(language_key))

    # Call the begin_analyze_actions method on your client,
    # passing in the joined call_contents as an array
    # and an AbstractiveSummaryAction with a sentence_count of 2.
    poller = client.begin_analyze_actions(
        [joined_call_contents],
        actions = [
            AbstractiveSummaryAction(sentence_count=2)
        ]
    )

    # Extract the summary sentences and merge them into a single summary string.
    for result in poller.result():
        summary_result = result[0]
        if summary_result.is_error:
            st.error(f'...Is an error with code "{summary_result.code}" and message "{summary_result.message}"')
            return ''

        abstractive_summary = " ".join([summary.text for summary in summary_result.summaries])

    # Return the summary as a JSON object in the shape '{"call-summary": abstractive_summary}'
    return json.loads('{"call-summary":"' + abstractive_summary + '"}')

@st.cache_data
def create_sentiment_analysis_and_opinion_mining_request(call_contents):
    """Analyze the sentiment of a call transcript and mine opinions. Key assumptions:
    - Azure Text Analytics endpoint and key stored in Streamlit secrets."""

    language_endpoint = st.secrets["language"]["endpoint"]
    language_key = st.secrets["language"]["key"]

    # The call_contents parameter is formatted as a list of strings.
    # Join them together with spaces to pass in as a single document.
    joined_call_contents = ' '.join(call_contents)

    # Create a Text Analytics Client
    client = TextAnalyticsClient(language_endpoint, AzureKeyCredential(language_key))

    # Analyze sentiment of call transcript, enabling opinion mining.
    result = client.analyze_sentiment([joined_call_contents], show_opinion_mining=True)

    # Retrieve all document results that are not an error.
    doc_result = [doc for doc in result if not doc.is_error]

    # The output format is a JSON document with the shape:
    # {
    #     "sentiment": document_sentiment,
    #     "sentiment-scores": {
    #         "positive": document_positive_score_as_two_decimal_float,
    #         "neutral": document_neutral_score_as_two_decimal_float,
    #         "negative": document_negative_score_as_two_decimal_float
    #     },
    #     "sentences": [
    #         {
    #             "text": sentence_text,
    #             "sentiment": document_sentiment,
    #             "sentiment-scores": {
    #                 "positive": document_positive_score_as_two_decimal_float,
    #                 "neutral": document_neutral_score_as_two_decimal_float,
    #                 "negative": document_negative_score_as_two_decimal_float
    #             },
    #             "mined_opinions": [
    #                 {
    #                     "target-sentiment": opinion_sentiment,
    #                     "target-text": opinion_target,
    #                     "target-scores": {
    #                         "positive": document_positive_score_as_two_decimal_float,
    #                         "neutral": document_neutral_score_as_two_decimal_float,
    #                         "negative": document_negative_score_as_two_decimal_float
    #                     },
    #                     "assessments": [
    #                       {
    #                         "assessment-sentiment": assessment_sentiment,
    #                         "assessment-text": assessment_text,
    #                         "assessment-scores": {
    #                             "positive": document_positive_score_as_two_decimal_float,
    #                             "negative": document_negative_score_as_two_decimal_float
    #                         }
    #                       }
    #                     ]
    #                 }
    #             ]
    #         }
    #     ]
    # }
    sentiment = {}

    # Assign the correct values to the JSON object.
    for document in doc_result:
        sentiment["sentiment"] = document.sentiment
        sentiment["sentiment-scores"] = {
            "positive": document.confidence_scores.positive,
            "neutral": document.confidence_scores.neutral,
            "negative": document.confidence_scores.negative
        }

        sentences = []
        for s in document.sentences:
            sentence = {}
            sentence["text"] = s.text
            sentence["sentiment"] = s.sentiment
            sentence["sentiment-scores"] = {
                "positive": s.confidence_scores.positive,
                "neutral": s.confidence_scores.neutral,
                "negative": s.confidence_scores.negative
            }

            mined_opinions = []
            for mined_opinion in s.mined_opinions:
                opinion = {}
                opinion["target-text"] = mined_opinion.target.text
                opinion["target-sentiment"] = mined_opinion.target.sentiment
                opinion["sentiment-scores"] = {
                    "positive": mined_opinion.target.confidence_scores.positive,
                    "negative": mined_opinion.target.confidence_scores.negative,
                }

                opinion_assessments = []
                for assessment in mined_opinion.assessments:
                    opinion_assessment = {}
                    opinion_assessment["text"] = assessment.text
                    opinion_assessment["sentiment"] = assessment.sentiment
                    opinion_assessment["sentiment-scores"] = {
                        "positive": assessment.confidence_scores.positive,
                        "negative": assessment.confidence_scores.negative
                    }
                    opinion_assessments.append(opinion_assessment)

                opinion["assessments"] = opinion_assessments
                mined_opinions.append(opinion)

            sentence["mined_opinions"] = mined_opinions
            sentences.append(sentence)

        sentiment["sentences"] = sentences

    return sentiment

@st.cache_data
def create_named_entity_extraction_request(call_contents):
    """Extract named entities from a call transcript. Key assumptions:
    - Azure Text Analytics endpoint and key stored in Streamlit secrets."""

    language_endpoint = st.secrets["language"]["endpoint"]
    language_key = st.secrets["language"]["key"]

    # The call_contents parameter is formatted as a list of strings.
    # Join them together with spaces to pass in as a single document.
    joined_call_contents = ' '.join(call_contents)

    # Create a Text Analytics Client
    client = TextAnalyticsClient(language_endpoint, AzureKeyCredential(language_key))

    # Recognize entities within the call transcript
    result = client.recognize_entities(documents=[joined_call_contents])[0]

    # Create named_entity list as a JSON array
    named_entities = []

    # Add each extracted named entity to the named_entity array.
    for entity in result.entities:
        named_entities.append({
            "text": entity.text,
            "category": entity.category,
            "subcategory": entity.subcategory,
            "length": entity.length,
            "offset": entity.offset,
            "confidence-score": entity.confidence_score
        })

    return named_entities

def make_azure_openai_embedding_request(text):
    """Create and return a new embedding request. Key assumptions:
    - Azure OpenAI endpoint, key, and deployment name stored in Streamlit secrets."""

    aoai_endpoint = st.secrets["aoai"]["endpoint"]
    aoai_key = st.secrets["aoai"]["key"]
    aoai_embedding_deployment_name = st.secrets["aoai"]["embedding_deployment_name"]

    client = openai.AzureOpenAI(
        api_key=aoai_key,
        api_version="2024-06-01",
        azure_endpoint = aoai_endpoint
    )
    # Create and return a new embedding request
    return client.embeddings.create(
        model=aoai_embedding_deployment_name,
        input=text
    )

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
    - Call contents is a list of strings.
    - Azure OpenAI endpoint, key, and deployment name stored in Streamlit secrets."""

    embeddings = []

    for content in call_contents:
        # Normalize the text for tokenization
        normalized_content = normalize_text(content)

        # Call make_azure_openai_embedding_request() with the normalized content
        response = make_azure_openai_embedding_request(normalized_content)

        # Append the response to the embeddings list
        embeddings.append(response)

    return embeddings

def save_embeddings_to_cosmos_db(embeddings):
    ## TODO: does this work?
    """Save embeddings to Cosmos DB vector store. Key assumptions:
    - Embeddings is a list of embeddings.
    - Cosmos DB endpoint, key, and database name stored in Streamlit secrets."""

    cosmos_endpoint = st.secrets["cosmos"]["endpoint"]
    cosmos_key = st.secrets["cosmos"]["key"]
    cosmos_database_name = st.secrets["cosmos"]["database_name"]

    # Create a CosmosClient
    client = tiktoken.CosmosClient(cosmos_endpoint, cosmos_key)

    # Create a database and a container
    client.create_database(cosmos_database_name)

    # Create a container
    client.create_container(cosmos_database_name, "embeddings")

    # Insert the embeddings into the container
    for embedding in embeddings:
        client.insert_document(cosmos_database_name, "embeddings", embedding)

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

def perform_saved_embeddings_to_cosmos_db():
    """Save embeddings to Cosmos DB vector store."""

    # Set call_contents to file_transcription_results.
    # If it is empty, write out an error message for the user.
    if 'file_transcription_results' in st.session_state:
        # Use st.spinner() to wrap the embeddings saving process.
        with st.spinner("Saving embeddings to Cosmos DB..."):
            # Call the generate_embeddings_for_call_contents function and set
            # its results to a variable named embeddings.
            ftr = st.session_state.file_transcription_results
            embeddings = generate_embeddings_for_call_contents(ftr)
            # Call the save_embeddings_to_cosmos_db function with the embeddings list.
            save_embeddings_to_cosmos_db(embeddings)
            st.session_state.embedding_status = "Embeddings successfully generated for this audio."

            # Call st.success() to indicate that the embeddings saving process is complete.
            if embeddings is not None:
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
            perform_saved_embeddings_to_cosmos_db()

        # Write the embedding_status value to the Streamlit dashboard.
        if 'embedding_status' in st.session_state:
            st.write(st.session_state.embedding_status)

if __name__ == "__main__":
    main()
