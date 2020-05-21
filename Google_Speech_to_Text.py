# -*- coding: utf-8 -*-
"""
Created on Fri May 15 12:42:58 2020

@author: Sunit
"""

'''

Using Google Speech to Text API
Asynchornous Request (Audio Files larger than 1 min)

'''

# import libraries
from pydub import AudioSegment
import io
import os
from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import enums, types
import wave
from google.cloud import storage
#files
filepath = "~/audio1/" #input audio file path
output_filepath = "~/transcripts/"
bucketname = "callsaudiofiles"


# UDF
#from mp3 to wav
def mpeg_to_wav(audio_file):
    if audio_file.split('.')[1] == 'mpeg':
        sound = AudioSegment.from_mpeg(audio_file)
        audio_file = audio_file.split('.')[0] + '.wav'
        sound.export(audio_file, format = 'wav')
        

def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")
    
    
def frame_rate_channel(audio_file):
    with wave.open(audio_file, 'rb') as wave_file:
        frame_ratee = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate, channels
    
    
#upload files to google cloud
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(source_file_name)


#Delete files in google cloud
def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()


#Transcribe
def google_transcribe(audio_file_name):
    
    file_name = filepath + audio_file
    mp3_to_wav(file_name)

    # The name of the audio file to transcribe
    
    frame_rate, channels = frame_rate_channel(file_name)
    
    if channels > 1:
        stereo_to_mono(file_name)
    
    bucket_name = bucketname
    source_file_name = filepath + audio_file
    destination_blob_name = audio_file
    
    upload_blob(bucket_name, source_file_name, destination_blob_name)
    
    gcs_uri = 'gs://' + bucketname + '/' + audio_file_name
    transcript = ''
    
    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)

    config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=frame_rate,
    language_code='en-US',
    enable_speaker_diarization=True,
    diarization_speaker_count=2) #Changed

    # Detects speech in the audio file
    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)
    result = response.results[-1] #Changed
    words_info = result.alternatives[0].words #Changed
    
    tag=1 #Changed
    speaker="" #Changed

    for word_info in words_info: #Changed
        if word_info.speaker_tag==tag: #Changed
            speaker=speaker+" "+word_info.word #Changed
        else: #Changed
            transcript += "speaker {}: {}".format(tag,speaker) + '\n' #Changed
            tag=word_info.speaker_tag #Changed
            speaker=""+word_info.word #Changed
 
    transcript += "speaker {}: {}".format(tag,speaker) #Changed
    
    delete_blob(bucket_name, destination_blob_name)
    return transcript

#Write transcripts
def write_transcripts(transcript_filename,transcript):
    f= open(output_filepath + transcript_filename,"w+")
    f.write(transcript)
    f.close()
    
    
#Execute
if __name__ == "__main__":
    for audio_file_name in os.listdir(filepath):
        transcript = google_transcribe(audio_file_name)
        transcript_filename = audio_file_name.split('.')[0] + '.txt'
        write_transcripts(transcript_filename,transcript)




























