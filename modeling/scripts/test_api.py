from transformers import AutoProcessor, BlipForConditionalGeneration
import torch
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import io

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
        # Read the image file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Process image with the model
        inputs = processor(images=image, return_tensors="pt").to(device)
        
        # Generate caption
        with torch.no_grad():
            # generate with default parameters
            outputs = model.generate(
                **inputs, 
                max_length=max_tokens,
                min_length=10,
                num_beams=6,  # try 6 beams for better performance
                num_return_sequences=2, # for number of generated captions
                temperature=1.0,
                top_k=50,
                top_p=0.9,
                repetition_penalty=1.2,
                length_penalty=1.0,
                no_repeat_ngram_size=2
            )
            captions = processor.batch_decode(outputs, skip_special_tokens=True)
        
        return {"caption": captions}
        
    except Exception as e:
        return {"error": str(e)}