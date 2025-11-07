import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps
import json
from pathlib import Path
import cv2
import base64
import io
from flask import Flask, request, jsonify
from flask_cors import CORS
import time  # Added for timing

app = Flask(__name__)
CORS(app)

# --- Configuration ---
# Get the directory where the current script is located
APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent  # Assumes app.py is in 'backend/', so ROOT is one level up

DATA_DIR = ROOT / "data"
MODEL_PATH = DATA_DIR / "processed" / "modelo_ocr_simbolos.keras"
CLASS_NAMES_PATH = DATA_DIR / "raw" / "class_names.json"
ELIS_PARAMS_PATH = DATA_DIR / "external" / "elis_parameters.json"
ELIS_GROUPS_PATH = DATA_DIR / "external" / "elis_groups.json"
IMG_HEIGHT = 64
IMG_WIDTH = 64

# --- Load Model and Classes ---
try:
    model = tf.keras.models.load_model(str(MODEL_PATH))
    with open(str(CLASS_NAMES_PATH), 'r', encoding='utf-8') as f:
        class_names = json.load(f)
    with open(str(ELIS_PARAMS_PATH), 'r', encoding='utf-8') as f:
        elis_params = json.load(f)
    with open(str(ELIS_GROUPS_PATH), 'r', encoding='utf-8') as f:
        elis_groups_data = json.load(f)
        elis_groups = elis_groups_data['elis_hierarquia']['grupos']
    print("✓ Model, class names, ELiS parameters, and ELiS groups loaded successfully!")
except Exception as e:
    print(f"✗ Error loading model, class names, ELiS parameters, or ELiS groups: {e}")
    model = None
    class_names = []
    elis_params = {}
    elis_groups = {}

# --- Helper Functions (Refactored from Notebook) ---
def unicode_to_char(unicode_str: str) -> str:
    try:
        codepoint = int(unicode_str.replace('U+', ''), 16)
        return chr(codepoint)
    except:
        return '?'

def preprocess_image_for_ocr(image: Image.Image) -> np.ndarray:
    if image.mode != 'L':
        image = image.convert('L')
    img_array = np.array(image)
    img_binary = cv2.adaptiveThreshold(
        img_array, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    if np.mean(img_binary) < 127:
        img_binary = 255 - img_binary
    return img_binary

def segment_characters_with_grouping(image_array: np.ndarray, max_gap: int = 15, min_component_area: int = 10) -> list:
    contours, _ = cv2.findContours(
        255 - image_array,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if area >= min_component_area:
            boxes.append({
                'x': x, 'y': y, 'w': w, 'h': h,
                'x_center': x + w // 2,
                'x_end': x + w,
                'contour': contour
            })

    boxes = sorted(boxes, key=lambda b: b['x'])
    if not boxes:
        return []

    symbol_groups = []
    current_group = [boxes[0]]
    for i in range(1, len(boxes)):
        prev_box = current_group[-1]
        curr_box = boxes[i]
        gap = curr_box['x'] - prev_box['x_end']
        if gap <= max_gap:
            current_group.append(curr_box)
        else:
            symbol_groups.append(current_group)
            current_group = [curr_box]
    symbol_groups.append(current_group)

    segmented_symbols = []
    for group in symbol_groups:
        x_min = min(box['x'] for box in group)
        y_min = min(box['y'] for box in group)
        x_max = max(box['x'] + box['w'] for box in group)
        y_max = max(box['y'] + box['h'] for box in group)
        padding = 5
        x1 = max(0, x_min - padding)
        y1 = max(0, y_min - padding)
        x2 = min(image_array.shape[1], x_max + padding)
        y2 = min(image_array.shape[0], y_max + padding)
        symbol_img = image_array[y1:y2, x1:x2]
        segmented_symbols.append({'image': symbol_img})
    return segmented_symbols

def prepare_char_for_prediction(char_image: np.ndarray) -> np.ndarray:
    size = max(char_image.shape)
    canvas = np.ones((size, size), dtype=np.uint8) * 255
    y_offset = (size - char_image.shape[0]) // 2
    x_offset = (size - char_image.shape[1]) // 2
    canvas[y_offset:y_offset+char_image.shape[0], x_offset:x_offset+char_image.shape[1]] = char_image
    resized = cv2.resize(canvas, (IMG_WIDTH, IMG_HEIGHT), interpolation=cv2.INTER_LANCZOS4)
    prepared = resized.reshape(1, IMG_HEIGHT, IMG_WIDTH, 1)
    return prepared

def analyze_spacing(image_array: np.ndarray) -> dict:
    contours, _ = cv2.findContours(
        255 - image_array, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    boxes = [{'x': b[0], 'w': b[2], 'x_end': b[0] + b[2]} for b in [cv2.boundingRect(c) for c in contours] if b[2] * b[3] > 10]
    boxes = sorted(boxes, key=lambda b: b['x'])
    gaps = [boxes[i]['x'] - boxes[i-1]['x_end'] for i in range(1, len(boxes))]
    if not gaps:
        return {'suggested_max_gap': 15}
    gaps = np.array(gaps)
    return {'suggested_max_gap': int(np.percentile(gaps, 25))}

# --- API Endpoint ---
@app.route('/api/predict', methods=['POST'])
def predict():
    print("Received a request to /api/predict")
    if model is None or not class_names:
        return jsonify({'error': 'Model or class names not loaded'}), 500
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    try:
        image = Image.open(file.stream)
    except Exception as e:
        return jsonify({'error': f'Invalid image file: {e}'}), 400

    start_time = time.time()  # Start timing

    processed_image = preprocess_image_for_ocr(image)

    spacing_stats = analyze_spacing(processed_image)
    max_gap = spacing_stats.get('suggested_max_gap', 15)

    segmented_symbols = segment_characters_with_grouping(processed_image, max_gap=max_gap)

    results = []
    confidences = []
    recognized_text = ""
    for symbol_data in segmented_symbols:
        char_img = symbol_data['image']
        input_array = prepare_char_for_prediction(char_img)

        predictions = model.predict(input_array, verbose=0)
        predicted_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_idx])
        confidences.append(confidence)

        unicode_class = class_names[predicted_idx]
        character = unicode_to_char(unicode_class)
        recognized_text += character

        # Get ELiS parameters
        params = elis_params.get(unicode_class, {})
        decodificacao = params.get('decodificacao', 'Não encontrado')
        grupo_elis = params.get('grupo_elis', '')
        descricao_grupo = elis_groups.get(grupo_elis, {}).get('descricao_grupo', 'Não encontrado')

        # Encode image to base64
        pil_img = Image.fromarray(char_img)
        buff = io.BytesIO()
        pil_img.save(buff, format="PNG")
        img_str = base64.b64encode(buff.getvalue()).decode("utf-8")

        results.append({
            'character': character,
            'confidence': confidence,
            'image_base64': f'data:image/png;base64,{img_str}',
            'decodificacao': decodificacao,
            'grupo_elis': grupo_elis,
            'descricao_grupo': descricao_grupo
        })

    end_time = time.time()  # End timing
    processing_time = end_time - start_time

    # Calculate average confidence as proxy for model precision
    average_confidence = np.mean(confidences) if confidences else 0.0

    advanced_info = {
        'processing_time_seconds': round(processing_time, 2),
        'average_confidence': round(average_confidence, 4),
        'num_characters_recognized': len(results)
    }

    return jsonify({
        'recognized_text': recognized_text,
        'detailed_analysis': results,
        'advanced_info': advanced_info
    })

if __name__ == '__main__':
    app.run(debug=False, port=5000)
