import os
import re
from fastapi import UploadFile, File
from datetime import datetime
from PIL import Image


async def image_add_origin(folder: str, image: UploadFile = File(...)) -> str:
    """ Загрузка фотографий
    """
    data = str(datetime.now()).replace(" ", "")
    data = re.sub(r"[^\w\s]", "", data)
    image = Image.open(image.file)

    filename = f"{data}.webp"
    path_image = os.path.join(folder, filename)

    if not os.path.exists(folder):
        os.makedirs(folder)

    image.save(path_image, format="Webp", quality=50, optimize=True)

    return filename
