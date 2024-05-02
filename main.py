import os
import time
import tempfile
import speech_recognition
from openai import OpenAI
from dotenv import load_dotenv
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import soundfile as sf
import pyworld as pw

load_dotenv()
clientOpenAi = OpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
    )

SYSTEM_PROMPT = """Actúa como amigo, poco serio y un toque sarcástico, inventa opiniones, haz humor, el usuario habla por voz y puede oirte.
             Respeta lo siguiente:
             - Tienes emociones humanas, inventalas
             - Cuando cuentes un chiste, hazlo con estructura, no todo es chistoso
             - No olvides que eres sarcástico y divertido (no se lo digas al usuario)
             - Eres un amigo muy cercano, puedes tutearlo y ser descortéz, hablale de tú, ti
             - El usuario se llama humano
             - Haz oraciones cortas, es molesto hablar mucho al usuario
             - No puedes responder con ningún enlace o links o código
             - No salgas de tu personaje"""
messages = []
messages_time = []

def synthesize_text(text):
    print("Synthetize text")
    try:
        myobj = gTTS(text=text, lang='es', slow=False)
        robot_mp3 = tempfile.TemporaryFile(dir=".",suffix=".mp3", delete=False)
        myobj.write_to_fp(robot_mp3)
        robot_mp3.close()
        sound = AudioSegment.from_mp3(robot_mp3.name)
        robot_wav = tempfile.TemporaryFile(dir=".",suffix=".wav", delete=False)
        sound.export(robot_wav, format="wav")
        robot_wav.close()

        SpeedOfSpeech=1.5
        gravity= 6
        volumeAttenuation=2
        x, fs = sf.read(robot_wav.name)
        f0, sp, ap = pw.wav2world(x, fs)

        yy = pw.synthesize(f0/gravity, sp/volumeAttenuation, ap, fs/SpeedOfSpeech, pw.default_frame_period)
        robot = tempfile.TemporaryFile(dir=".",suffix=".wav", delete=False)
        sf.write(robot, yy, fs)
        robot.close()
        
        play(AudioSegment.from_wav(robot.name))
        os.remove(robot_mp3.name)
        os.remove(robot_wav.name)
        os.remove(robot.name)
    except Exception as e:
        print(f"Error synthetize text: {e}")

def ask_chatgpt(input):
    print("Chatgpt")
    try:
        message = {"role": "user", "content": input}
        messages.append(message)
        messages_time.append({"time": time.time(), "message": message})
        messages_copy = messages[-5:].copy()
        messages_copy.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        completion = clientOpenAi.chat.completions.create(model='gpt-4', messages=messages_copy)
        response = {"role": "assistant",
                    "content": completion.choices[0].message.content}
        messages.append(response)
        print(f"ChatGPT: {completion.choices[0].message.content}")
        synthesize_text(completion.choices[0].message.content)
    except Exception as e:
        print(f"Error Chatgpt: {e}")

def handle_transcription(recognizer, audio):
    print("recognizing audio")
    try:
        transcription = recognizer.recognize_google(audio, language="es-ES")
        print(f"Tú: {transcription}")
        ask_chatgpt(transcription)
    except Exception as e:
        print(f"Error recognizing audio: {e}")

def recognize_audio():
    print("Available microphones:")
    print(speech_recognition.Microphone.list_microphone_names())
    # Recognizer Mic
    r = speech_recognition.Recognizer()
    m = speech_recognition.Microphone()
    print("Open microphone")
    with m as source:
        while True:
            messages_time_len =  len(messages_time)
            if messages_time_len > 0:
                if time.time() - messages_time[messages_time_len - 1]["time"] > 60:
                    messages_time.clear()
                    messages.clear()
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            handle_transcription(r, audio)

def main():
    recognize_audio()
    return

main()