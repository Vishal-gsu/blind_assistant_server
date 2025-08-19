import cv2
import pyttsx3
from PIL import Image
import numpy as np
import time

# Initialize TTS engine
engine = pyttsx3.init()

def load_ocr_model():
    """Check if we can use Tesseract OCR"""
    try:
        import pytesseract
        
        # Set Tesseract path for Windows installation
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\HUNTER\AppData\Local\Tesseract-OCR\tesseract.exe',
        ]
        
        # Try to find Tesseract
        for path in possible_paths:
            try:
                import os
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    print(f"Found Tesseract at: {path}")
                    version = pytesseract.get_tesseract_version()
                    print(f"Tesseract version: {version}")
                    return True
            except:
                continue
        
        # If not found in standard locations, try without explicit path
        try:
            version = pytesseract.get_tesseract_version()
            print(f"Tesseract found in PATH, version: {version}")
            return True
        except:
            print("Tesseract not found. Please install Tesseract OCR.")
            return False
            
    except ImportError:
        print("pytesseract not installed")
        return False

def speak(text):
    """Speak the given text with better settings"""
    print(f"[OCR Speaking]: {text}")
    
    # Set speech rate for better comprehension
    engine.setProperty('rate', 150)  # Slower speech for blind users
    engine.setProperty('volume', 0.9)  # High volume
    
    engine.say(text)
    engine.runAndWait()
    time.sleep(0.3)  # Brief pause after speaking



def capture_multiple_shots():
    """Take multiple shots automatically and return the best result"""
    speak("Text recognition starting. Hold the camera towards the text.")
    speak("I'll take several pictures automatically to get the best result.")
    speak("Try to hold the device steady and ensure good lighting.")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("Error: Could not access camera.")
        return None
    
    # Set camera properties for better quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    
    # Give camera time to adjust
    time.sleep(3)
    
    best_text = ""
    shots = 8  # Increased shots for better results
    all_results = []
    
    for shot in range(shots):
        speak(f"Taking picture {shot + 1} of {shots}")
        
        # Take multiple frames and use the sharpest one
        frames = []
        for _ in range(3):
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
            time.sleep(0.1)
        
        if frames:
            # Use the last frame (usually sharpest after auto-focus)
            frame = frames[-1]
            
            # Save frame for debugging
            cv2.imwrite(f'debug_frame_{shot}.jpg', frame)
            
            text = extract_text_from_image(frame)
            print(f"Shot {shot + 1} detected: '{text}'")
            
            if text and text.strip():
                all_results.append(text.strip())
                if len(text.strip()) > len(best_text.strip()):
                    best_text = text
                    # Give brief feedback but don't overwhelm with speech
                    if len(text.strip()) > 3:  # Only announce if meaningful
                        print(f"Good detection found: {text}")
                        speak("Good text found")
        
        time.sleep(1.2)  # Slightly shorter wait
    
    cap.release()
    
    # Analyze all results to find the most complete one
    if all_results:
        # Remove duplicates and find the most meaningful result
        unique_results = list(set(all_results))
        
        # Find the longest result that's not just single words
        meaningful_results = [r for r in unique_results if len(r.split()) > 1 or len(r) > 5]
        
        if meaningful_results:
            best_text = max(meaningful_results, key=len)
        else:
            best_text = max(unique_results, key=len)
        
        print(f"All results: {all_results}")
        print(f"Unique results: {unique_results}")
        print(f"Best result selected: '{best_text}'")
        
        speak(f"Analysis complete. Best detection: {best_text[:50]}")
        return best_text
    else:
        speak("No text detected in any of the pictures. Please ensure the text is clearly visible and well-lit.")
        return None

def preprocess_image_for_ocr(image):
    """Preprocess image for better OCR results."""
    try:
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        return enhanced
    except Exception as e:
        print(f"Preprocessing error: {e}")
        return image

def extract_text_from_image(image):
    """Extract text from image using simple and effective methods"""
    try:
        # Convert OpenCV image to PIL if needed
        if isinstance(image, np.ndarray):
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            pil_image = Image.fromarray(image_rgb)
        else:
            pil_image = image
        
        best_text = ""
        
        # Try with Tesseract if available
        if load_ocr_model():
            try:
                import pytesseract
                
                # Use a general-purpose PSM mode
                text = pytesseract.image_to_string(pil_image, config='--psm 6').strip()
                text = ' '.join(text.split())  # Clean up whitespace
                
                if text:
                    best_text = text
                    print(f"Tesseract: '{text}'")
                        
            except Exception as e:
                print(f"Tesseract OCR failed: {e}")
        
        # If Tesseract didn't work well, try with preprocessing
        if not best_text or len(best_text) < 3:
            print("Trying with image preprocessing...")
            
            # Apply preprocessing to improve OCR
            processed_image = preprocess_image_for_ocr(image)
            
            try:
                # Convert back to PIL
                if len(processed_image.shape) == 2:
                    proc_img_rgb = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2RGB)
                else:
                    proc_img_rgb = processed_image
                
                pil_proc = Image.fromarray(proc_img_rgb)
                
                if load_ocr_model():
                    import pytesseract
                    text = pytesseract.image_to_string(pil_proc, config='--psm 6').strip()
                    text = ' '.join(text.split())
                    
                    if text and len(text) > len(best_text):
                        best_text = text
                        print(f"Preprocessed image: '{text}'")
                            
            except Exception as e:
                print(f"Preprocessing attempt failed: {e}")
        
        # Clean and validate the final result
        if best_text:
            # Remove common OCR artifacts
            cleaned_text = best_text.replace('|', 'I').replace('{', '').replace('}', '')
            cleaned_text = cleaned_text.replace('»', '').replace('§', 'S').replace('æ', 'ae')
            cleaned_text = ' '.join(cleaned_text.split())  # Clean whitespace
            
            # Check if result looks like real text (not just symbols)
            letter_count = sum(1 for c in cleaned_text if c.isalpha())
            if letter_count >= 2:  # At least 2 letters
                print(f"Final cleaned result: '{cleaned_text}'")
                return cleaned_text
            else:
                print(f"Result '{cleaned_text}' doesn't look like valid text")
                return "No clear text detected"
        else:
            return "No text detected"
    
    except Exception as e:
        print(f"OCR Error: {e}")
        return None

def read_text_from_camera():
    """Main function to capture image and read text - accessible for blind users"""
    try:
        speak("Starting text recognition. For best results:")
        speak("Hold the card flat, ensure good lighting, and point the camera directly at the text.")
        
        text = capture_multiple_shots()
        
        if text and text.strip() and not text.startswith("No"):
            # Clean up the text and make it more readable
            cleaned_text = text.replace('\n', ' ').replace('\r', ' ')
            cleaned_text = ' '.join(cleaned_text.split())  # Remove extra spaces
            
            speak("Text detection complete.")
            time.sleep(0.5)  # Brief pause
            speak(f"I detected the following text: {cleaned_text}")
            
            # Also print for debugging
            print(f"Final detected text: '{cleaned_text}'")
            return cleaned_text
        else:
            speak("No clear text was detected. Try these tips:")
            speak("Hold the card closer, ensure it's flat, check the lighting, and make sure text is right-side up.")
            return None
            
    except Exception as e:
        speak("Sorry, there was an error with text recognition.")
        print(f"OCR Error: {e}")
        return None



