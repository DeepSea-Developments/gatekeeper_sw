# gatekeeper_sw

- Create .env file from .env.example

- Install dependencies with pip install -r requirements.txt

- run python mainv2.py

## Notes

- Check if ffmpeg is installed on the operating system

## How to run in windows

1. install python and check is include in the path of the system.

2. After try to run any python script you must have installed the c++ debug tools. Go to https://visualstudio.microsoft.com/es/visual-cpp-build-tools/
and download the visual studio tools.

Once debug tools are installed open it and select the following minimal packages:

- MSVC C++ compilation tools.

- C++ cmake tools for windows.

- Mainly characteristics of test tools.

- C++ clang tools for windows

3. Try to install the packages included in requirements.txt, if any of the packages fails its installation then install them manually one by one.

Usually shows missing packages with pyworld, openai, setuptools, dotenv and SpeechRecognition.

4. Install ffmpeg following the tutorial here: 

https://es.wikihow.com/instalar-FFmpeg-en-Windows