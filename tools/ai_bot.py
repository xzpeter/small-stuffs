#!/usr/bin/env python3
import os
import warnings
import json
import subprocess
import requests

# Hide annoying warning logs
# os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
# os.environ["MLX_WHISPER_LOG_LEVEL"] = "ERROR"
# warnings.filterwarnings("ignore")

import speech_recognition as sr
import mlx_whisper
import soundfile as sf
from mlx_audio.tts.utils import load_model

# ================= Configuration =================
STT_MODEL = "mlx-community/whisper-large-v3-turbo"

# Lite 版本，速度更快，内存占用小
# QWEN_TTS_MODEL = "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16"
# Pro 版本，质量更高，内存需求约3-4GB
QWEN_TTS_MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16"

# Options: "中文女声"、"中文男声"、"Vivien"、"Soji"
VOICE_NAME = "中文女声" 
OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "qwen2.5" 

# Timeout to stop recording if silent
MIC_TIMEOUT = 5
# Max seconds to record my voice
MIC_TIME_LIMIT = 60
# How many seconds are allowed to pause when speaking
MIC_PAUSE_THRESHOLD = 2
# =================================================

print("🧠 Loading AI Models into M4 Unified Memory... (Takes a few seconds)")
recognizer = sr.Recognizer()
recognizer.pause_threshold = MIC_PAUSE_THRESHOLD
tts_model = load_model(QWEN_TTS_MODEL) # 如果你的 load_model 函数支持传入模型路径

def listen_to_mic(filename="user_input.wav"):
    """Automatically records audio when you speak and stops when you are silent."""
    with sr.Microphone() as source:
        print("\n🎤 Adjusting for background noise... (1 second)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("🟢 Listening! You can speak now...")

        try:
            audio_data = recognizer.listen(source, timeout=MIC_TIMEOUT,
                                           phrase_time_limit=MIC_TIME_LIMIT)
            with open(filename, "wb") as f:
                f.write(audio_data.get_wav_data())
            return True
        except sr.WaitTimeoutError:
            return False

def transcribe(filename="user_input.wav"):
    """Converts the recorded audio file to text."""
    print("⏳ Transcribing...")
    result = mlx_whisper.transcribe(
        filename, 
        path_or_hf_repo=STT_MODEL, 
        task="transcribe" # Keeps it in Chinese so Ollama reads Chinese natively
    )
    return result["text"].strip()

def ask_ai(text):
    """Sends the transcribed text to Ollama running locally."""
    print(f"🗣️ You: {text}")
    print("🤖 Thinking...")

    # We prompt Ollama to keep answers short so the TTS generates fast
    payload = {
        "model": LLM_MODEL,
        "prompt": f"You are a helpful voice assistant. Keep your response brief, natural, and conversational. Reply ONLY in Chinese. User says: {text}",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        reply = response.json().get("response", "")
        print(f"💬 AI: {reply}")
        return reply
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return "抱歉，我的大脑好像没连接上。" # "Sorry, my brain seems disconnected."

def speak(text, filename="ai_output.wav"):
    print("🔊 Qwen3-TTS Generating voice...")
    try:
        for result in tts_model.generate(text, voice=VOICE_NAME, language="Chinese"):
            sf.write(filename, result.audio, 24000)
        subprocess.call(["afplay", filename])
    except Exception as e:
        print(f"TTS Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("\n" + "="*40)
    print("🚀 M4 Local Voice Assistant Started!")
    print("Press Ctrl+C to stop the program at any time.")
    print("="*40)

    while True:
        try:
            # Step 1: Listen to the mic
            if not listen_to_mic():
                continue # If no speech detected, loop back and listen again

            # Step 2: STT (Speech to Text)
            user_text = transcribe()
            if not user_text:
                continue

            # Step 3: LLM (Text to Text)
            ai_reply = ask_ai(user_text)

            # Step 4: TTS (Text to Speech)
            speak(ai_reply)

        except KeyboardInterrupt:
            print("\n🛑 Exiting the AI Voice Assistant. Goodbye!")
            break
        except Exception as e:
            print(f"\n⚠️ System Error: {e}")

if __name__ == "__main__":
    main()
