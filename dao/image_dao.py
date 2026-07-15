import os
from datetime import datetime

from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_FOLDER = os.path.join(BASE_DIR, "static", "images")

ALLOWED_TYPES = {"png", "jpg", "jpeg", "webp"}


def save_quest_image(file):
    if not file or not file.filename:
        return False, "Please choose an image."

    extension = file.filename.rsplit(".", 1)[-1].lower()
    if extension not in ALLOWED_TYPES:
        return False, "Image must be png, jpg or webp."

    os.makedirs(IMAGE_FOLDER, exist_ok=True)

    image = Image.open(file)
    image = image.convert("RGB")
    image.thumbnail((800, 400))

    filename = f"{int(datetime.now().timestamp())}.jpg"
    full_path = os.path.join(IMAGE_FOLDER, filename)
    image.save(full_path)

    image_url = f"/static/images/{filename}"
    return True, image_url