from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

# Load your local image file
image = Image.open('OCR-Example-e1513085924797-1030x713.jpg').convert("RGB")

# Initialize the processor and model
# processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
# model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')

# Process the image
pixel_values = processor(images=image, return_tensors="pt").pixel_values

# Generate text from the image
generated_ids = model.generate(pixel_values)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

print("Recognized text:", generated_text)