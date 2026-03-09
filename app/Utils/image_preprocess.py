from PIL import Image
import numpy as np


def preprocess_image(image: Image.Image, target_size=(224, 224)):
    image = image.convert("RGB")
    image = image.resize(target_size)

    img_array = np.array(image).astype("float32") / 255.0

    img_array = np.expand_dims(img_array, axis=0)

    return img_array