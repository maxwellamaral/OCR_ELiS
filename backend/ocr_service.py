import tensorflow as tf
import numpy as np
import json
from pathlib import Path
from PIL import Image

class OCRService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCRService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.ROOT = self._find_project_root()
        self.MODEL_SAVE_PATH = self.ROOT / "data" / "processed" / "modelo_ocr_simbolos.keras"
        self.CLASS_NAMES_PATH = self.ROOT / "data" / "raw" / "class_names.json"

        self.model = self._load_model()
        self.class_names = self._load_class_names()
        self.IMG_HEIGHT = 64
        self.IMG_WIDTH = 64
        self._initialized = True

    def _find_project_root(self, markers=("pyproject.toml", ".git")) -> Path:
        p = Path.cwd().resolve()
        for parent in [p, *p.parents]:
            if any((parent / m).exists() for m in markers):
                return parent
        return p

    def _load_model(self):
        try:
            model = tf.keras.models.load_model(self.MODEL_SAVE_PATH)
            print("Model loaded successfully.")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def _load_class_names(self):
        try:
            with open(self.CLASS_NAMES_PATH, 'r', encoding='utf-8') as f:
                class_names = json.load(f)
            print(f"Class names loaded: {len(class_names)} classes.")
            return class_names
        except Exception as e:
            print(f"Error loading class names: {e}")
            return None

    def predict(self, image_array):
        if self.model is None or self.class_names is None:
            return {"error": "Model or class names not loaded."}

        try:
            # Preprocess the image array
            img = Image.fromarray(image_array).convert('L') # Convert to grayscale
            img = img.resize((self.IMG_WIDTH, self.IMG_HEIGHT))

            input_arr = tf.keras.preprocessing.image.img_to_array(img)
            if input_arr.ndim == 2:
                input_arr = np.expand_dims(input_arr, axis=-1)
            input_arr = np.expand_dims(input_arr, axis=0) # Add batch dimension

            # Perform prediction
            predictions = self.model.predict(input_arr)

            # Post-process the result
            predicted_idx = np.argmax(predictions)
            predicted_class = self.class_names[predicted_idx]
            confidence = float(predictions[0][predicted_idx])

            return {
                "predicted_class": predicted_class,
                "confidence": confidence,
            }

        except Exception as e:
            return {"error": f"Prediction failed: {e}"}

# Singleton instance
ocr_service = OCRService()
