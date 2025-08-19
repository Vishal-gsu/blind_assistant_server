# check_mic.py
import speech_recognition as sr

def test_microphone():
    """A simple script to test microphone input and configuration."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Microphone check script running.")
        print("Please wait a moment while I adjust for ambient noise...")
        
        # This helps the recognizer adapt to your environment
        r.adjust_for_ambient_noise(source, duration=2)
        print("\n" + "="*40)
        print("Mic is calibrated. Please say something clearly.")
        print("="*40 + "\n")

        try:
            # Listen for audio
            audio = r.listen(source, timeout=5)
            print("I heard something! Processing...")

            # Recognize the audio
            text = r.recognize_google(audio)
            print(f"\nSUCCESS! I heard you say: '{text}'\n")
            print("Your microphone is working correctly with the speech_recognition library.")

        except sr.WaitTimeoutError:
            print("\nERROR: I didn't hear anything. The listen operation timed out.")
            print("Troubleshooting: Make sure your microphone is not muted and is selected as the default system input.")
        except sr.UnknownValueError:
            print("\nERROR: Google Speech Recognition could not understand the audio.")
            print("Troubleshooting: Try speaking more clearly or reducing background noise.")
        except sr.RequestError as e:
            print(f"\nERROR: Could not request results from Google service; {e}")
            print("Troubleshooting: Check your internet connection.")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    test_microphone()