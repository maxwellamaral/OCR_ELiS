from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import base64
import cv2
from ocr_service import ocr_service
from segmentation_service import segmentation_service

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return "OCR Sign Analysis Backend is running!"

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # 1. Segment the image into individual signs
            sign_images = segmentation_service.segment_signs(filepath)

            if not sign_images:
                return jsonify({"error": "No signs detected in the image."}), 400

            results = []
            for i, sign_img_array in enumerate(sign_images):
                # 2. Get prediction for each sign
                prediction = ocr_service.predict(sign_img_array)

                # 3. Encode the segmented image to send back to the frontend
                _, buffer = cv2.imencode('.png', sign_img_array)
                img_base64 = base64.b64encode(buffer).decode('utf-8')

                results.append({
                    "sign_index": i,
                    "prediction": prediction,
                    "image": img_base64
                })

            return jsonify({"analysis": results})

        finally:
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
