import settings
import helpers
from fastapi import FastAPI, UploadFile, File
import redis
import uuid
import time
import json
import io

from google.cloud import translate_v2 as translate

# Initialize Google Translate client
translate_client = translate.Client()


# initialize application and Redis server
app = FastAPI()
db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

@app.get("/")
async def homepage():
	return "WEB SERVER!"

@app.post("/generate")
async def generate(file: UploadFile = File(...)):
    # initialize the data dictionary that will be returned from the view
    response = {"success": False}

    # read the image in PIL format and prepare it for
    contents = await file.read()
    byte_image = io.BytesIO(contents).getvalue()

    # generate an ID for the generation then add the request id + image
    k = str(uuid.uuid4())
    base64_image = helpers.base64_encode_image(byte_image)
    d = {"id": k, "image": base64_image}
    db.rpush(settings.IMAGE_QUEUE, json.dumps(d))

    # keep looping until our model server returns the output captions
    while True:
        # attempt to grab the output predictions
        output = db.get(k)

        # check to see if our model has classified the input
        # image
        if output is not None:
            # add the output predictions to our data
            # dictionary so we can return it to the client
            output = output.decode("utf-8")
            response['caption'] = output

            # delete the result from the database and break from the polling loop
            db.delete(k)
            break

        # sleep for a small amount to give the model a chance to generate image caption
        time.sleep(settings.CLIENT_SLEEP)

    # indicate that the request was a success
    response["success"] = True

    return response

@app.post("/generate_vn")
async def generate_vn(file: UploadFile = File(...)):
    # initialize the data dictionary that will be returned from the view
    response = {"success": False}

    # read the image in PIL format and prepare it for
    contents = await file.read()
    byte_image = io.BytesIO(contents).getvalue()

    # generate an ID for the generation then add the request id + image
    k = str(uuid.uuid4())
    base64_image = helpers.base64_encode_image(byte_image)
    d = {"id": k, "image": base64_image}
    db.rpush(settings.IMAGE_QUEUE, json.dumps(d))

    # keep looping until our model server returns the output captions
    while True:
        # attempt to grab the output predictions
        output = db.get(k)

        # check to see if our model has classified the input
        # image
        if output is not None:
            # add the output predictions to our data
            # dictionary so we can return it to the client
            output = output.decode("utf-8")

            # trasnlate to vietnamese
            translation = translate_client.translate(
                output,
                target_language='vi',
                source_language='en'
            )
            response['caption'] = translation
            
            # delete the result from the database and break from the polling loop
            db.delete(k)
            break

        # sleep for a small amount to give the model a chance to generate image caption
        time.sleep(settings.CLIENT_SLEEP)

    # indicate that the request was a success
    response["success"] = True

    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000)
