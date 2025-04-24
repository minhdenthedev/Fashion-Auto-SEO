from transformers import AutoProcessor, BlipForConditionalGeneration
import torch
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import io
from google.cloud import translate_v2 as translate


# Initialize Google Translate client
translate_client = translate.Client()

# load the model and processor
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
processor = AutoProcessor.from_pretrained('kzap201/fashion_BLIP', revision='v1.0')  # change to version='v1.0' for the latest version
model = BlipForConditionalGeneration.from_pretrained('kzap201/fashion_BLIP', revision='v1.0')
model.to(device)
model.eval()

app = FastAPI()

@app.post("/generate")
async def generate_caption(file: UploadFile = File(...), max_tokens: int = 100):
    try:
        # Read file once
        contents = await file.read()

        # Process image with the model using the same contents
        image = Image.open(io.BytesIO(contents))
        inputs = processor(images=image, return_tensors="pt").to(device)
        
        # Generate caption
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_length=max_tokens,
                min_length=10,
                num_beams=6,  # higher beam yield better result but more computation
                num_return_sequences=2,
                temperature=1.0,
                top_k=50,
                top_p=0.9,
                repetition_penalty=1.2,
                length_penalty=1.0,
                no_repeat_ngram_size=2
            )
            english_captions = processor.batch_decode(outputs, skip_special_tokens=True)
            
            # Translate captions to Vietnamese
            vietnamese_captions = []
            for caption in english_captions:
                translation = translate_client.translate(
                    caption,
                    target_language='vi',
                    source_language='en'
                )
                vietnamese_captions.append(translation['translatedText'])
            
            return {
                "english_captions": english_captions,
                "vietnamese_captions": vietnamese_captions
            }
        
    except Exception as e:
        return {"error": str(e)}