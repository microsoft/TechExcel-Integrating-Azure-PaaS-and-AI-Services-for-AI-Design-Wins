import streamlit as st
import streamlit_extras.stateful_button as stx
from streamlit_js_eval import streamlit_js_eval
import requests
import pandas as pd
import json
import openai
import inspect
import time
from scipy.io import wavfile
import azure.cognitiveservices.speech as speechsdk

st.set_page_config(layout="wide")

with open('config_full.json') as f:
    config = json.load(f)

aoai_endpoint = config['AOAIEndpoint']
aoai_api_key = config['AOAIKey']
deployment_name = config['AOAIDeploymentName']
speech_key = config['SpeechKey']
speech_region = config['SpeechRegion']


### Exercise 05: Provide live audio transcription
def create_transcription_request(audio_file, speech_key, speech_region, speech_recognition_language="en-US"):
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
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done= True

    # Subscribe to the events fired by the conversation transcriber
    transcriber.transcribed.connect(handle_final_result)
    transcriber.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    transcriber.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    transcriber.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
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

def create_live_transcription_request(speech_key, speech_region, speech_recognition_language="en-US"):
    # Creates speech configuration with subscription information
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language=speech_recognition_language
    transcriber = speechsdk.transcription.ConversationTranscriber(speech_config)

    done = False

    def handle_final_result(evt):
        all_results.append(evt.result.text)
        print(evt.result.text)

    all_results = []

    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous transcription upon receiving an event `evt`"""
        print('CLOSING {}'.format(evt))
        nonlocal done
        done = True

    # Subscribe to the events fired by the conversation transcriber
    transcriber.transcribed.connect(handle_final_result)
    transcriber.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    transcriber.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    transcriber.canceled.connect(lambda evt: print('CANCELLED {}'.format(evt)))
    # stop continuous transcription on either session stopped or canceled events
    transcriber.session_stopped.connect(stop_cb)
    transcriber.canceled.connect(stop_cb)

    transcriber.start_transcribing_async()

    # Streamlit refreshes the page on each interaction,
    # so a clean start and stop isn't really possible with button presses.
    # Instead, we're constantly updating transcription results, so that way,
    # when the user clicks the button to stop, we can just stop updating the results.
    # This might not capture the final message, however, if the user stops before
    # we receive the message--we won't be able to call the stop event.
    while not done:
        st.session_state.transcription_results = all_results
        time.sleep(1)

    return

def make_compliance_chat_request(system, call_contents):
    # Create an Azure OpenAI client.
    client = openai.AzureOpenAI(
        base_url=f"{aoai_endpoint}/openai/deployments/{deployment_name}/",
        api_key=aoai_api_key,
        api_version="2023-12-01-preview"
    )

    # Create and return a new chat completion request
    return client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": call_contents}
        ],
    )

def is_call_in_compliance(call_contents, include_recording_message, is_relevant_to_topic):
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
        You are an automated analysis system for Contoso Suites. Contoso Suites is a luxury hotel and resort chain with locations
        in a variety of Caribbean nations and territories.
        
        You are analyzing a call for relevance and compliance.

        You will only answer the following questions based on the call contents:
        1. Was there vulgarity on the call?
        {include_recording_message_text}
        {is_relevant_to_topic_text}
    """

    response = make_compliance_chat_request(system, joined_call_contents)
    return response.choices[0].message.content


### Exercise 06: Generate call summary


def main():
    call_contents = []
    st.write(
    """
    # Call Center

    This Streamlit dashboard is intended to replicate some of the functionality of a call center monitoring solution. It is not intended to be a production-ready application.
    """
    )

    st.write("## Simulate a Call")

    uploaded_file = st.file_uploader("Upload an audio file", type="wav")
    if uploaded_file is not None and ('file_transcription' not in st.session_state or st.session_state.file_transcription is False):
        st.audio(uploaded_file, format='audio/wav')
        with st.spinner("Transcribing the call..."):
            all_results = create_transcription_request(uploaded_file, speech_key, speech_region)
            st.session_state.file_transcription_results = all_results
            st.session_state.file_transcription = True
        st.success("Transcription complete!")

    if 'file_transcription_results' in st.session_state:
        st.write(st.session_state.file_transcription_results)
        
    st.write("## Perform a Live Call")

    start_recording = stx.button("Record", key="recording_in_progress")
    if start_recording:
        with st.spinner("Transcribing your conversation..."):
            create_live_transcription_request(speech_key, speech_region)

    if 'transcription_results' in st.session_state:
        st.write(st.session_state.transcription_results)

    st.write("""
    ## Clear Messages between Calls

    Select this button to clear out session state and refresh the page.

    Do this before loading a new audio file or recording a new call. This will ensure that transcription and compliance checks will happen correctly.
    """)

    if st.button("Clear messages"):
        if 'file_transcription_results' in st.session_state:
            del st.session_state.file_transcription_results
        if 'transcription_results' in st.session_state:
            del st.session_state.transcription_results
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

    st.write("## Is Your Call in Compliance?")

    include_recording_message = st.checkbox("Call needs an indicator we are recording it")
    is_relevant_to_topic = st.checkbox("Call is relevant to the hotel and resort industry")

    if st.button("Check for Compliance"):
        with st.spinner("Checking for compliance..."):
            if 'file_transcription_results' in st.session_state:
                call_contents = st.session_state.file_transcription_results
            elif 'transcription_results' in st.session_state:
                call_contents = st.session_state.transcription_results
            else:
                st.write("Please upload an audio file or record a call before checking for compliance.")
            if call_contents is not None and len(call_contents) > 0:
                compliance_results = is_call_in_compliance(call_contents, include_recording_message, is_relevant_to_topic)
                st.write(compliance_results)
        st.success("Compliance check complete!")

if __name__ == "__main__":
    main()
