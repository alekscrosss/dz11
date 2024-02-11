# файл image_upload.py

import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()  #

cloudinary.config(
  cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
  api_key = os.getenv('CLOUDINARY_API_KEY'),
  api_secret = os.getenv('CLOUDINARY_API_SECRET')
)


def upload_image(image_file):

    result = cloudinary.uploader.upload(image_file)
    return result['url']