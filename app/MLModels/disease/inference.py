import numpy as np
from pathlib import Path

try:
    import tensorflow as tf
except ImportError:
    tf = None

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "aloe_model.tflite"
LABELS_PATH = BASE_DIR / "labels.txt"


def load_labels():
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


labels = load_labels()


class TFLiteDiseaseModel:
    def __init__(self):
        if tf is None:
            raise ImportError(
                "TensorFlow is not installed. Install tensorflow or tflite-runtime."
            )

        self.interpreter = tf.lite.Interpreter(model_path=str(MODEL_PATH))
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict(self, processed_image: np.ndarray):
        input_data = np.array(processed_image, dtype=np.float32)

        self.interpreter.set_tensor(self.input_details[0]["index"], input_data)
        self.interpreter.invoke()

        output_data = self.interpreter.get_tensor(self.output_details[0]["index"])[0]

        predicted_index = int(np.argmax(output_data))
        confidence = float(output_data[predicted_index])

        return {
            "disease": labels[predicted_index],
            "confidence": round(confidence, 4),
            "all_scores": {
                labels[i]: float(round(score, 4))
                for i, score in enumerate(output_data)
            },
        }


model_instance = TFLiteDiseaseModel()


def predict_disease(processed_image: np.ndarray):
    return model_instance.predict(processed_image)