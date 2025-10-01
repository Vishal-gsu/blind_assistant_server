import cv2
from PIL import Image
import numpy as np

def load_ocr_model():
    """Check if we can use Tesseract OCR"""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except ImportError:
        print("pytesseract not installed")
        return False
    except pytesseract.TesseractNotFoundError:
        print("Tesseract not found. Please install Tesseract OCR and ensure it's in your PATH.")
        return False

def preprocess_image_for_ocr(image):
    """Preprocess image for better OCR results."""
    try:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        return enhanced
    except Exception as e:
        print(f"Preprocessing error: {e}")
        return image

def extract_text_from_image(image):
    """Extract text from image using simple and effective methods"""
    try:
        if isinstance(image, np.ndarray):
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            pil_image = Image.fromarray(image_rgb)
        else:
            pil_image = image
        
        best_text = ""
        
        if load_ocr_model():
            try:
                import pytesseract
                
                text = pytesseract.image_to_string(pil_image, config='--psm 6').strip()
                text = ' '.join(text.split())
                
                if text:
                    best_text = text
                        
            except Exception as e:
                print(f"Tesseract OCR failed: {e}")
        
        if not best_text or len(best_text) < 3:
            processed_image = preprocess_image_for_ocr(image)
            
            try:
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
                            
            except Exception as e:
                print(f"Preprocessing attempt failed: {e}")
        
        if best_text:
            cleaned_text = best_text.replace('|', 'I').replace('{', '').replace('}', '')
            cleaned_text = cleaned_text.replace('»', '').replace('§', 'S').replace('æ', 'ae')
            cleaned_text = ' '.join(cleaned_text.split())
            
            letter_count = sum(1 for c in cleaned_text if c.isalpha())
            if letter_count >= 2:
                return cleaned_text
            else:
                return "No clear text detected"
        else:
            return "No text detected"
    
    except Exception as e:
        print(f"OCR Error: {e}")
        return None

def read_text_from_frame(frame):
    """Main function to capture image and read text - accessible for blind users"""
    try:
        text = extract_text_from_image(frame)
        
        if text and text.strip() and not text.startswith("No"):
            cleaned_text = text.replace('\n', ' ').replace('\r', ' ')
            cleaned_text = ' '.join(cleaned_text.split())
            return cleaned_text
        else:
            return None
            
    except Exception as e:
        print(f"OCR Error: {e}")
        return None