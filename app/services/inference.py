import numpy as np
import tensorflow as tf

from app.utils.image_preprocess import preprocess_image

MODEL_PATH = "app/model/aloe_model.tflite"
LABELS_PATH = "app/model/labels.txt"

interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

with open(LABELS_PATH, "r") as f:
    LABELS = [line.strip() for line in f.readlines()]

def predict(image):
    processed = preprocess_image(image)

    interpreter.set_tensor(input_details[0]["index"], processed)
    interpreter.invoke()

    output = interpreter.get_tensor(output_details[0]["index"])[0]
    confidence = float(np.max(output))
    class_index = int(np.argmax(output))

    return {
        "disease": LABELS[class_index],
        "confidence": round(confidence * 100, 2)
    }
