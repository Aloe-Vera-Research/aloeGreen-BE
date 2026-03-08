from PIL import Image
import numpy as np

def preprocess_image(image: Image.Image):
    image = image.convert("RGB")
    image = image.resize((224, 224))   # change ONLY if your model differs
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image.astype(np.float32)
