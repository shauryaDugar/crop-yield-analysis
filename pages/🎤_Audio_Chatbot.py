import streamlit as st
import speech_recognition as sr
from googlesearch import search
# from transformers import pipeline
import requests
from bs4 import BeautifulSoup
import logging
from deep_translator import GoogleTranslator
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import re
import os
from dotenv import load_dotenv
from st_audiorec import st_audiorec

load_dotenv()

st.set_page_config("Audio Chatbot", page_icon=":microphone:")

# Function number 1
def transcribe_audio(audio_data):
    recognizer = sr.Recognizer()
    # Convert audio bytes to AudioFile object

    # Convert audio bytes to a file-like object
    audio_file = BytesIO(audio_data)

    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)  # Read the entire audio file

    try:
        # this uses the google speech API for different languages. Generally not used in production,
        # but it will do for our purpose as it eliminates the need for Google Cloud Authentication which
        # is quite troublesome
        text = recognizer.recognize_google(audio, language="hi-IN")
        return text
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand the audio"
    except sr.RequestError as e:
        return "Could not request results from Google Speech Recognition service; {0}".format(e)
    
# Function number 2
def translate_to_english(text, source_language):
   if text is None:
       return "Unable to translate: No input text"
   try:
       translator = GoogleTranslator(source=source_language, target='en')
       translation = translator.translate(text)
       return translation
   except Exception as e:
       logging.error(f"Error during translation: {e}")
       return "Unable to translate due to an error"
   
# function number 3
# does simple google searches and gets the top links
def search_google(query):
    results = []
    for j in search(query, num=5, stop=5, pause=2):
        results.append(j)
    return results

# Settings for LLM
# gemini API
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
 
# configuring the model
generation_config = {
   "temperature": 1,
   "top_p": 0.95,
   "top_k": 64,
   "max_output_tokens": 8192,
   "response_mime_type": "text/plain",
}
 
safety_settings = [
   {
       "category": "HARM_CATEGORY_HARASSMENT",
       "threshold": "BLOCK_MEDIUM_AND_ABOVE",
   },
   {
       "category": "HARM_CATEGORY_HATE_SPEECH", 
       "threshold": "BLOCK_MEDIUM_AND_ABOVE",
   },
   {
       "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
       "threshold": "BLOCK_MEDIUM_AND_ABOVE", 
   },
   {
       "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
       "threshold": "BLOCK_MEDIUM_AND_ABOVE",
   },
]
 
# actually creates the LLM responsible for giving the output
gemini_model = genai.GenerativeModel(
   model_name="gemini-1.5-flash-latest", 
   safety_settings=safety_settings,
   generation_config=generation_config,
)

# function number 4
def generate_content_with_LLM(prompt):
    try:
        response = gemini_model.generate_content(prompt)
        output = response.text
        return output
    except Exception as e:
        logging.error(f"Error during content generation - {e}")
        return "Encoutered error, please try again later!"

# function number 5 to translate back into regional language
def translate_to_regional_language(text, target_language):
   try:
       translator = GoogleTranslator(source='en', target=target_language)
       translation = translator.translate(text)
       return translation
   except Exception as e:
       logging.error(f"Error during translation to regional language: {e}")
       return "Unable to translate to regional language due to an error"
   

# function number 5  
def text_to_speech(text, language):
    cleaned_text = remove_emojis_and_symbols(text)
    try:
        tts = gTTS(text=cleaned_text, lang=language)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        logging.error(f"Error during text-to-speech conversion: {e}")
        return None
    
# helper function to remove emojis and symbols from the regional language output text
def remove_emojis_and_symbols(text):
    emoji_pattern = re.compile("["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)
    

def main():
    st.title("Regional Language Audio Chatbot with Google Search and Summarization")

    st.write("Speak in Marathi and the chatbot will transcribe your speech. It will also display search results based on your speech along with summaries of each link.")


    wav_audio_data = st_audiorec()

    if wav_audio_data is not None:

        # Transcribe speech to text
        text = transcribe_audio(wav_audio_data)

        # display transcribed text
        if text:
            st.success(f"You said: {text}")
        else:
            st.error("Text could not be transcribed")

        st.info("Translating text to English...")

        # using fn2
        english_text = translate_to_english(text, "mr")
        st.success(f"Translated Query: {english_text}")

        # fn3
        # call the google search method and display relevant links
        results = search_google(english_text)
        with st.expander("Google Search Results Lists:"):
            for i, result in enumerate(results, start=1):
                st.write(f"{i}. {result}")
                # # Extract text from link
                # extracted_text = extract_text_from_link(result)

        st.info("Prompting an LLM to generate output...")

        # fn4
        llm_output = generate_content_with_LLM(english_text)
        st.write(llm_output)

        # fn5
        regional_output = translate_to_regional_language(llm_output, 'mr')
        st.write(regional_output)

        # fn6
        audio_bytes = text_to_speech(regional_output, 'mr')
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", start_time=0)
        else:
            st.warning("Unable to generate audio for the answer.")



if __name__ == "__main__":
    main()
