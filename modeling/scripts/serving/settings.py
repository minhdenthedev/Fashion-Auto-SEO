# initialize Redis connection settings
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# initialize constants used for server queuing
IMAGE_QUEUE = "image_queue"
BATCH_SIZE = 4
SERVER_SLEEP = 0.25
CLIENT_SLEEP = 0.25
IMAGE_DTYPE = 'float32'

# model config
MODEL_NAME = 'kzap201/fashion_BLIP'
VERSION = 'v1.0'