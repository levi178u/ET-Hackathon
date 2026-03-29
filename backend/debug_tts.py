try:
    from gtts import gTTS
    print("gTTS is available")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
