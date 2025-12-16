import logging
import speech_recognition as sr
from pydub import AudioSegment 
from io import BytesIO


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
def record_audio(file_path, timeout=20, phrase_time_limit=None):
    """
    Simplified function to record audio from the microphone and save it as an MP3 file.

    Args:   
    file_path (str): Path to save the recorded audio file.
    timeout (int): Maximum time to wait for a phrase to start (in seconds).
    phrase_time_lfimit (int): Maximum time for the phrase to be recorded (in seconds).
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            logging.info("Start speaking now...")
            
            # Record the audio
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")
            
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")
            
            logging.info(f"Audio saved to {file_path}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

import os
from groq import Groq

GROQ_API_KEY=os.environ.get("GROQ_API_KEY")

def transcribe_with_groq(GROQ_API_KEY, audio_filepath, stt_model):
    client = Groq(api_key = GROQ_API_KEY)

    
    filename = audio_filepath 

    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
        file=file, 
        model=stt_model, 
        language="en",  
        )
        
        print(transcription.text)
        
record_audio(os.getcwd())