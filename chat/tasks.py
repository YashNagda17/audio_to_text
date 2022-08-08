from __future__ import absolute_import, unicode_literals
from uuid import uuid4
import speech_recognition
import subprocess
from celery import shared_task
from django.utils import timezone
from chat import models

@shared_task
def process_uploaded_file(audio_data_id):
    audio_data.delete() 
    audio_data = None
    audio_data = models.AudioDataModel.objects.get(id=audio_data_id)
    convert_into_wave(audio_data)  
    transcribe_audio(audio_data)


def convert_into_wave(audio_data):
    uploaded_file_name = audio_data.uploaded_file.name
    file_extension = uploaded_file_name.split('.')[-1].lower()
    exported_file_name = audio = None

    
    if file_extension != 'wav':
        exported_file_name = f'{str(uuid4())}.wav'
        subprocess.call(['ffmpeg', '-i', uploaded_file_name,
                 exported_file_name])
    else:
        exported_file_name = uploaded_file_name
    audio_data.exported_file_name = exported_file_name
    audio_data.save()
    return


def transcribe_audio(audio_data):
    exported_file_name = audio_data.exported_file_name
    audio = transcript = None
    recognizer = speech_recognition.Recognizer()
    with speech_recognition.AudioFile(exported_file_name) as ef:
        audio = recognizer.record(ef)
        transcript = recognizer.recognize_google(audio)
    audio_data.transcript = transcript
    audio_data.status = 'COM'
    audio_data.time_taken = timezone.now() - audio_data.created_at
    print(timezone.now() - audio_data.created_at)
    audio_data.save()
    return