import cv2
import numpy as np

class SegmentationService:
    def segment_signs(self, image_path, padding=10):
        """
        Segments an image to find and extract individual signs.

        :param image_path: Path to the input image.
        :param padding: Padding to add around each extracted sign.
        :return: A list of extracted sign images (as numpy arrays).
        """
        try:
            # Read the image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Image not found or unable to read.")

            # Convert to grayscale and apply binary threshold
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Filter contours based on area and sort them from left to right
            min_contour_area = 100 # Adjust as needed
            valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]

            # Get bounding boxes and sort by the x-coordinate
            bounding_boxes = [cv2.boundingRect(cnt) for cnt in valid_contours]
            bounding_boxes.sort(key=lambda b: b[0])

            extracted_signs = []
            for (x, y, w, h) in bounding_boxes:
                # Add padding
                x_pad = max(0, x - padding)
                y_pad = max(0, y - padding)
                w_pad = w + (2 * padding)
                h_pad = h + (2 * padding)

                # Extract the sign with padding
                sign_roi = image[y_pad:y_pad+h_pad, x_pad:x_pad+w_pad]
                extracted_signs.append(sign_roi)

            return extracted_signs

        except Exception as e:
            print(f"Error during segmentation: {e}")
            return []

# Singleton instance
segmentation_service = SegmentationService()
