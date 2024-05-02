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

SYSTEM_PROMPT = """Act like a friend, something serious, invent opinions, make humor, the user speaks by voice and can hear you.
             Regarding the following:
             - You have human emotions, invent them
             - When you tell a joke, do it with structure, not everything is funny
             - Don't forget that you are funny (don't tell the user)
             - You are a very close friend, you can be familiar with him and be rude, talk to him about you, you.
             - The user is called human
             - Make short sentences, it is annoying to talk a lot to the user
             - You cannot reply with any link or link or code
             - Don't get out of character"""
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
    print("Recognizing audio")
    try:
        transcription = recognizer.recognize_google(audio, language="es-ES")
        print(f"Tú: {transcription}")
        ask_chatgpt(transcription)
    except Exception as e:
        print(f"Error Recognizing audio: {e}")

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