import queue
import time
import pydub
import streamlit as st
import speech_recognition as sr
from streamlit_webrtc import WebRtcMode, webrtc_streamer

@st.cache_data
def get_ice_servers():
    return [{"urls": ["stun:stun.l.google.com:19302"]}]

def app_sst():
    recognizer = sr.Recognizer()

    if "transcribed_text" not in st.session_state:
        st.session_state.transcribed_text = ""

    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        rtc_configuration={"iceServers": get_ice_servers()},
        media_stream_constraints={"video": False, "audio": True},
    )

    status_indicator = st.empty()
    text_output = st.empty()

    if not webrtc_ctx.state.playing:
        return

    status_indicator.write("Running. Say something!")

    while webrtc_ctx.state.playing:
        if webrtc_ctx.audio_receiver:
            sound_chunk = pydub.AudioSegment.empty()
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                time.sleep(0.1)
                status_indicator.write("No frame arrived.")
                continue

            for audio_frame in audio_frames:
                sound = pydub.AudioSegment(
                    data=audio_frame.to_ndarray().tobytes(),
                    sample_width=audio_frame.format.bytes,
                    frame_rate=audio_frame.sample_rate,
                    channels=len(audio_frame.layout.channels),
                )
                sound_chunk += sound

            if len(sound_chunk) > 0:
                sound_chunk = sound_chunk.set_channels(1).set_frame_rate(16000)
                audio_data = sr.AudioData(sound_chunk.raw_data, 16000, 2)
                
                try:
                    text = recognizer.recognize_google(audio_data)
                    st.session_state.transcribed_text += text + " "
                    text_output.markdown(f"**Text:** {st.session_state.transcribed_text}")
                except sr.UnknownValueError:
                    text_output.markdown(f"**Text:** {st.session_state.transcribed_text} [Unrecognized]")
                except sr.RequestError as e:
                    text_output.markdown(f"**Text:** {st.session_state.transcribed_text} [Request Error: {e}]")
        else:
            status_indicator.write("AudioReceiver is not set. Abort.")
            break

    st.markdown(f"**Final Text:** {st.session_state.transcribed_text}")

st.header("Real Time Speech-to-Text")
st.markdown(
    """
This demo app is using the [speech_recognition](https://pypi.org/project/SpeechRecognition/) library
to convert speech to text in real-time.
"""
)

app_sst()

if st.session_state.transcribed_text:
    st.write(st.session_state.transcribed_text)

st.session_state.transcribed_text = ""