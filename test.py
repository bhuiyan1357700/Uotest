import os
from dotenv import load_dotenv

load_dotenv()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'firebase_config.json'

from google.cloud import vision

client = vision.ImageAnnotatorClient()
print("✅ Vision API credentials loaded successfully!")