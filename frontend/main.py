import sys
import requests
import base64
from io import BytesIO
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QScrollArea, QGridLayout,
    QSizePolicy, QFileDialog
)
from PySide6.QtGui import QPixmap, QIcon, QFont, QFontDatabase, QColor, QPalette, QImage
from PySide6.QtCore import Qt, QSize
from PIL import Image

BACKEND_URL = "http://127.0.0.1:5000"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ELiS - Reconhecimento OCR")
        self.setGeometry(100, 100, 1400, 900)
        self.selected_image_path = None
        self.setAcceptDrops(True)

        # Set dark theme
        self.set_dark_theme()

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Title
        title_layout = QVBoxLayout()
        title = QLabel("Libras Sign Writing OCR")
        title.setFont(QFont("Space Grotesk", 36, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Carregue uma imagem para análise e revisão educacional.")
        subtitle.setFont(QFont("Space Grotesk", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #A0A0A0;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        main_layout.addLayout(title_layout)

        # Main content area (2 columns)
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Column 1: Image Analysis
        analysis_container, analysis_layout = self.create_container("1. Imagem para Análise")
        content_layout.addWidget(analysis_container)

        # --- Drag and Drop Area ---
        self.create_drag_drop_area(analysis_layout)

        # --- Image Preview ---
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(600, 200)
        self.image_preview.setStyleSheet("background-color: black; border: 1px solid #333333; border-radius: 8px;")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setText("Image Preview")
        analysis_layout.addWidget(self.image_preview, alignment=Qt.AlignCenter)

        # --- OCR Button ---
        self.ocr_button = QPushButton("Realizar OCR")
        self.ocr_button.setFont(QFont("Space Grotesk", 14, QFont.Bold))
        self.ocr_button.setStyleSheet("""
            QPushButton {
                background-color: #D87A63; color: white; padding: 12px;
                border: none; border-radius: 8px;
            }
            QPushButton:hover { background-color: #C76A53; }
        """)
        self.ocr_button.clicked.connect(self.perform_ocr)
        analysis_layout.addWidget(self.ocr_button, alignment=Qt.AlignCenter)


        # Column 2: Results and Review
        results_container, results_layout = self.create_container("2. Resultados e Revisão")
        content_layout.addWidget(results_container)

        # --- OCR Result ---
        results_layout.addWidget(QLabel("Resultado do OCR"))
        self.ocr_result_input = QLineEdit()
        self.ocr_result_input.setReadOnly(True)
        results_layout.addWidget(self.ocr_result_input)

        # --- Manual Correction ---
        results_layout.addWidget(QLabel("Correção Manual (Opcional)"))
        correction_layout = QHBoxLayout()
        self.manual_input = QLineEdit()
        self.manual_input.setPlaceholderText("Digite os caracteres aqui...")
        correction_layout.addWidget(self.manual_input)
        process_button = QPushButton("Processar")
        process_button.setStyleSheet("background-color: #E9C46A; color: #121212;")
        process_button.clicked.connect(self.process_manual_correction)
        correction_layout.addWidget(process_button)
        results_layout.addLayout(correction_layout)

        # --- Detailed Analysis ---
        results_layout.addSpacing(20)
        analysis_title = QLabel("Análise Detalhada dos Sinais")
        analysis_title.setFont(QFont("Space Grotesk", 16, QFont.Bold))
        results_layout.addWidget(analysis_title)

        self.sign_grid = QGridLayout()
        self.sign_grid.setSpacing(15)
        results_layout.addLayout(self.sign_grid)
        results_layout.addStretch()


    def create_header(self):
        header_widget = QFrame()
        header_widget.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 12px; padding: 10px;")
        header_layout = QHBoxLayout(header_widget)

        title_label = QLabel("ELiS - Reconhecimento OCR")
        title_label.setFont(QFont("Space Grotesk", 18, QFont.Bold))

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(QPushButton("About"))
        return header_widget

    def create_container(self, title):
        container = QFrame()
        container.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 12px; padding: 20px;")
        layout = QVBoxLayout(container)

        title_label = QLabel(title)
        title_label.setFont(QFont("Space Grotesk", 20, QFont.Bold))
        title_label.setStyleSheet("border: none; border-bottom: 1px solid #333333; padding-bottom: 10px; margin-bottom: 10px;")
        layout.addWidget(title_label)

        return container, layout

    def create_drag_drop_area(self, parent_layout):
        dd_area = QFrame()
        dd_area.setFrameShape(QFrame.StyledPanel)
        dd_area.setStyleSheet("border: 2px dashed #333333; border-radius: 8px;")

        dd_layout = QVBoxLayout(dd_area)
        dd_layout.setAlignment(Qt.AlignCenter)
        dd_layout.setSpacing(15)

        dd_layout.addWidget(QLabel("Arraste e solte uma imagem aqui, ou clique para selecionar", alignment=Qt.AlignCenter))
        dd_layout.addWidget(QLabel("Imagens com 5 a 10 caracteres horizontais.", alignment=Qt.AlignCenter, styleSheet="color: #A0A0A0;"))

        upload_button = QPushButton("Upload")
        upload_button.setFixedWidth(200)
        upload_button.clicked.connect(self.open_image_file)
        dd_layout.addWidget(upload_button, alignment=Qt.AlignCenter)

        parent_layout.addWidget(dd_area)

    def open_image_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            self.load_image(file_name)

    def load_image(self, file_path):
        self.selected_image_path = file_path
        pixmap = QPixmap(file_path)
        self.image_preview.setPixmap(pixmap.scaled(self.image_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def perform_ocr(self):
        if not self.selected_image_path:
            self.ocr_result_input.setText("Please select an image first.")
            return

        try:
            with open(self.selected_image_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{BACKEND_URL}/analyze", files=files)

            if response.status_code == 200:
                result = response.json()
                self.update_sign_analysis(result.get("analysis", []))
            else:
                self.ocr_result_input.setText(f"Error: {response.text}")
        except Exception as e:
            self.ocr_result_input.setText(f"Failed to connect to backend: {e}")

    def update_sign_analysis(self, analysis_results):
        # Clear existing widgets
        for i in reversed(range(self.sign_grid.count())):
            self.sign_grid.itemAt(i).widget().setParent(None)

        if not analysis_results:
            self.ocr_result_input.setText("No signs detected.")
            return

        predicted_text = ""
        for i, result in enumerate(analysis_results):
            sign_widget = QWidget()
            sign_layout = QVBoxLayout(sign_widget)

            # Decode and display the image
            img_data = base64.b64decode(result['image'])
            q_img = QImage.fromData(img_data, "PNG")
            pixmap = QPixmap.fromImage(q_img)

            sign_image = QLabel()
            sign_image.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            sign_image.setFixedSize(100, 100)
            sign_image.setStyleSheet("background-color: #2a2a2a; border: 1px solid #333333; border-radius: 8px;")
            sign_image.setAlignment(Qt.AlignCenter)

            # Display the prediction
            prediction = result['prediction']
            predicted_class = prediction.get('predicted_class', 'N/A')
            predicted_text += f"[{predicted_class}] "

            sign_label = QLabel(predicted_class)
            sign_label.setAlignment(Qt.AlignCenter)

            sign_layout.addWidget(sign_image)
            sign_layout.addWidget(sign_label)

            self.sign_grid.addWidget(sign_widget, 0, i)

        self.ocr_result_input.setText(predicted_text.strip())

    def process_manual_correction(self):
        corrected_text = self.manual_input.text()
        if corrected_text:
            self.ocr_result_input.setText(corrected_text)
            # Here you could also send the correction back to the backend to improve the model

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                self.load_image(file_path)

    def set_dark_theme(self):
        self.setFont(QFont("Space Grotesk", 12))

        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(18, 18, 18))
        dark_palette.setColor(QPalette.WindowText, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.Base, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.ToolTipText, QColor(18, 18, 18))
        dark_palette.setColor(QPalette.Text, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.Button, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ButtonText, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(138, 154, 91))
        dark_palette.setColor(QPalette.Highlight, QColor(138, 154, 91))
        dark_palette.setColor(QPalette.HighlightedText, QColor(18, 18, 18))
        self.setPalette(dark_palette)

        self.setStyleSheet("""
            QWidget {
                color: #E0E0E0;
                background-color: #121212;
                font-family: 'Space Grotesk';
            }
            QLineEdit {
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 8px;
                background-color: #1E1E1E;
            }
            QPushButton {
                background-color: #8A9A5B;
                color: #121212;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7A8A4B;
            }
            QFrame {
                border: none;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
