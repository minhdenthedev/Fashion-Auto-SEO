from transformers import AutoProcessor, BlipForConditionalGeneration
import torch
import settings
import redis
import time
import json
from PIL import Image
from io import BytesIO

# connect to Redis server
db = redis.StrictRedis(host=settings.REDIS_HOST,
	port=settings.REDIS_PORT, db=settings.REDIS_DB)

# load model and processor
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
processor = AutoProcessor.from_pretrained(settings.MODEL_NAME, revision=settings.VERSION)
model = BlipForConditionalGeneration.from_pretrained(settings.MODEL_NAME, revision=settings.VERSION)
model.to(device)
model.eval()

def generate_caption():
    # continually pool for new images to classify
    while True:
        # attempt to grab a batch of images from the database, then
        # initialize the image IDs and batch of images themselves
        queue = db.lrange(settings.IMAGE_QUEUE, 0,
            settings.BATCH_SIZE - 1)
        imageIDs = []
        batch = []

		# loop over the queue
        for q in queue:
            # deserialize the object and obtain the input image
            q = json.loads(q.decode("utf-8"))
            # Decode base64 image data 
            import base64
            decoded_image = base64.b64decode(q['image'])
            image = Image.open(BytesIO(decoded_image)).convert('RGB')
            batch.append(image)
            imageIDs.append(q["id"])

        # check to see if we need to process the batch
        if len(imageIDs) > 0:
            # Process image with the model
            inputs = processor(images=image, return_tensors="pt").to(device)
            
            # Generate caption
            with torch.no_grad():
                # generate with default parameters
                outputs = model.generate(
                    **inputs, 
                    max_length=100,
                    min_length=10,
                    num_beams=5,  # try 6 beams for better performance
                    num_return_sequences=1, # for number of generated captions
                    temperature=1.0,
                    top_k=50,
                    top_p=0.9,
                    repetition_penalty=1.2,
                    length_penalty=1.0,
                    no_repeat_ngram_size=2
                )
                captions = processor.batch_decode(outputs, skip_special_tokens=True)

            # loop over the image IDs and their corresponding set of
            # results from our model
            for (imageID, caption) in zip(imageIDs, captions):
                db.set(imageID, caption)

            # remove the set of images from our queue
            db.ltrim(settings.IMAGE_QUEUE, len(imageIDs), -1)

        # sleep for a small amount
        time.sleep(settings.SERVER_SLEEP)

# if this is the main thread of execution start the model server
# process
if __name__ == "__main__":
	generate_caption()


