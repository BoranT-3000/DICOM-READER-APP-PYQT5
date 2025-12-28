import sys
import numpy as np
import requests
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QPushButton, QLabel, QComboBox, QSlider,
                           QFileDialog, QMessageBox, QGroupBox, QFormLayout,
                           QSplitter, QScrollArea, QMenuBar, QAction, QStatusBar,
                           QInputDialog, QLineEdit, QTextEdit, QTabWidget,
                           QCheckBox, QSpinBox, QColorDialog, QFrame, QDialog,
                           QTextBrowser, QTableWidget, QTableWidgetItem, QHeaderView,
                           QShortcut) # YENI: QShortcut eklendi
from PyQt5.QtCore import Qt, QTimer, QSettings, QThread, pyqtSignal, QDateTime # YENI: QDateTime eklendi
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont, QKeySequence, QTextCursor, QTextCharFormat, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Try to import required libraries
try:
    import pydicom
    PYDICOM_AVAILABLE = True
except ImportError:
    PYDICOM_AVAILABLE = False

try:
    import nibabel as nib
    NIBABEL_AVAILABLE = True
except ImportError:
    NIBABEL_AVAILABLE = False

class AIThread(QThread):
    """AI processing thread for non-blocking AI operations"""
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key, prompt):
        super().__init__()
        self.api_key = api_key
        self.prompt = prompt

    def run(self):
        try:
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': self.api_key
            }

            data = {
                'contents': [{
                    'parts': [{
                        'text': self.prompt
                    }]
                }]
            }

            response = requests.post(
                'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                ai_text = result['candidates'][0]['content']['parts'][0]['text']
                self.result_ready.emit(ai_text)
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                self.error_occurred.emit(f"Gemini API error: {error_msg}")

        except Exception as e:
            self.error_occurred.emit(f"Error generating AI report: {str(e)}")


class PatientReportDialog(QDialog):
    """Dialog for patient report creation"""
    def __init__(self, patient_info, image_info, parent=None):
        super().__init__(parent)
        self.patient_info = patient_info
        self.image_info = image_info
        self.report_text = ""
        self.ai_suggestion = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Patient Report")
        self.setGeometry(200, 200, 1000, 700)

        layout = QVBoxLayout(self)

        # Patient info section
        patient_group = QGroupBox("Patient Information")
        patient_layout = QFormLayout(patient_group)

        self.patient_name_edit = QLineEdit(self.patient_info.get('name', ''))
        self.patient_id_edit = QLineEdit(self.patient_info.get('id', ''))
        self.study_date_edit = QLineEdit(self.patient_info.get('date', ''))
        self.modality_edit = QLineEdit(self.patient_info.get('modality', ''))

        patient_layout.addRow("Patient Name:", self.patient_name_edit)
        patient_layout.addRow("Patient ID:", self.patient_id_edit)
        patient_layout.addRow("Study Date:", self.study_date_edit)
        patient_layout.addRow("Modality:", self.modality_edit)

        layout.addWidget(patient_group)

        # Image info section
        image_group = QGroupBox("Image Information")
        image_layout = QFormLayout(image_group)

        self.image_desc_edit = QLineEdit(self.image_info.get('description', ''))
        self.windowing_edit = QLineEdit(f"WC: {self.image_info.get('wc', 40)}, WW: {self.image_info.get('ww', 80)}")

        image_layout.addRow("Image Description:", self.image_desc_edit)
        image_layout.addRow("Windowing:", self.windowing_edit)

        layout.addWidget(image_group)

        # Report section
        report_group = QGroupBox("Your Report")
        report_layout = QVBoxLayout(report_group)

        self.report_edit = QTextEdit()
        self.report_edit.setPlaceholderText("Write your medical report here...")
        report_layout.addWidget(self.report_edit)

        layout.addWidget(report_group)

        # AI suggestion section
        ai_group = QGroupBox("AI Suggestion")
        ai_layout = QVBoxLayout(ai_group)

        self.ai_suggestion_edit = QTextEdit()
        self.ai_suggestion_edit.setPlaceholderText("AI suggestion will appear here...")
        self.ai_suggestion_edit.setReadOnly(True)
        ai_layout.addWidget(self.ai_suggestion_edit)

        ai_btn_layout = QHBoxLayout()
        self.generate_ai_btn = QPushButton("🤖 Generate AI Suggestion")
        self.generate_ai_btn.clicked.connect(self.generate_ai_suggestion)
        ai_btn_layout.addWidget(self.generate_ai_btn)

        self.apply_ai_btn = QPushButton("✅ Apply AI Suggestion")
        self.apply_ai_btn.clicked.connect(self.apply_ai_suggestion)
        self.apply_ai_btn.setEnabled(False)
        ai_btn_layout.addWidget(self.apply_ai_btn)

        ai_layout.addLayout(ai_btn_layout)
        layout.addWidget(ai_group)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save Report")
        self.save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def generate_ai_suggestion(self):
        """Generate AI suggestion for the report"""
        # This would typically call the AI API
        # For demo purposes, we'll simulate it
        self.generate_ai_btn.setText("⏳ Generating...")
        self.generate_ai_btn.setEnabled(False)

        # Simulate AI processing
        QTimer.singleShot(2000, self.simulate_ai_response)

    def simulate_ai_response(self):
        """Simulate AI response"""
        ai_text = f"""Based on the {self.modality_edit.text()} image with windowing parameters {self.windowing_edit.text()}:

Key Findings:
- Normal anatomical structures are well visualized
- No acute pathological findings observed
- Image quality is adequate for diagnostic interpretation

Clinical Implications:
- Findings are within normal limits
- No immediate intervention required

Recommendations:
- Routine follow-up as clinically indicated
- Consider additional sequences if further evaluation needed"""

        self.ai_suggestion_edit.setPlainText(ai_text)
        self.ai_suggestion = ai_text
        self.apply_ai_btn.setEnabled(True)
        self.generate_ai_btn.setText("🤖 Generate AI Suggestion")
        self.generate_ai_btn.setEnabled(True)

    def apply_ai_suggestion(self):
        """Apply AI suggestion to report"""
        current_text = self.report_edit.toPlainText()
        if current_text:
            current_text += "\n\n" + self.ai_suggestion
        else:
            current_text = self.ai_suggestion
        self.report_edit.setPlainText(current_text)

    def get_report_data(self):
        """Get report data"""
        return {
            'patient_name': self.patient_name_edit.text(),
            'patient_id': self.patient_id_edit.text(),
            'study_date': self.study_date_edit.text(),
            'modality': self.modality_edit.text(),
            'image_description': self.image_desc_edit.text(),
            'windowing': self.windowing_edit.text(),
            'report': self.report_edit.toPlainText()
        }

# --- YENI SINIF: AIChatDialog ---
class AIChatDialog(QDialog):
    """Dialog for AI chat functionality"""
    def __init__(self, patient_info, image_info, api_key, parent=None):
        super().__init__(parent)
        self.patient_info = patient_info
        self.image_info = image_info
        self.api_key = api_key
        self.chat_history = [] # Store conversation history
        self.ai_thread = None

        # Load window geometry from settings
        self.settings = QSettings("MedicalViewer", "EnhancedViewer")
        geometry = self.settings.value("ai_chat_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(800, 600)

        self.setWindowTitle("🤖 AI Chat")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Chat history display
        self.chat_history_display = QTextEdit()
        self.chat_history_display.setReadOnly(True)
        # Set a monospace font for better readability of code/output if needed
        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        self.chat_history_display.setFont(font)
        layout.addWidget(self.chat_history_display)

        # Input area
        input_layout = QHBoxLayout()
        self.user_input = QTextEdit()
        self.user_input.setMaximumHeight(100) # Limit height
        self.user_input.setPlaceholderText("Type your message here...\nPress Ctrl+Enter to send.")
        # Allow Ctrl+Enter to send message
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self.user_input)
        shortcut.activated.connect(self.send_message)
        input_layout.addWidget(self.user_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Initial context message
        initial_context = self._generate_initial_context()
        self._append_message("System", initial_context, "info")

    def _generate_initial_context(self):
        """Generate initial context message for the AI."""
        context = "Context provided for the conversation:\n"
        context += f"- Patient Name: {self.patient_info.get('name', 'N/A')}\n"
        context += f"- Patient ID: {self.patient_info.get('id', 'N/A')}\n"
        context += f"- Study Date: {self.patient_info.get('date', 'N/A')}\n"
        context += f"- Modality: {self.patient_info.get('modality', 'N/A')}\n"
        context += f"- Image Description: {self.image_info.get('description', 'N/A')}\n"
        context += f"- Windowing (WC/WW): {self.image_info.get('wc', 'N/A')} / {self.image_info.get('ww', 'N/A')}\n"
        context += "\nYou can now ask questions about this case or general medical topics."
        return context

    def _append_message(self, sender, message, msg_type="user"):
        """Append a message to the chat history display."""
        cursor = self.chat_history_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        if cursor.position() > 0:
            cursor.insertText("\n") # Add a newline before new messages

        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        formatted_message = f"[{timestamp}] {sender}: {message}"

        # Apply simple formatting based on message type
        char_format = QTextCharFormat()
        if msg_type == "user":
            char_format.setForeground(QColor("lightblue" if self.parent().dark_mode else "blue"))
            char_format.setFontWeight(QFont.Bold)
        elif msg_type == "ai":
            char_format.setForeground(QColor("lightgreen" if self.parent().dark_mode else "darkgreen"))
        elif msg_type == "info":
            char_format.setForeground(QColor("gray"))
            char_format.setFontItalic(True)
        elif msg_type == "error":
            char_format.setForeground(QColor("red"))
            char_format.setFontWeight(QFont.Bold)

        cursor.insertText(formatted_message, char_format)
        cursor.insertText("\n") # Add newline after the message
        self.chat_history_display.setTextCursor(cursor)
        self.chat_history_display.ensureCursorVisible() # Scroll to bottom

        # Store in history list
        self.chat_history.append({"sender": sender, "message": message, "type": msg_type})

    def send_message(self):
        """Send user message to AI."""
        user_message = self.user_input.toPlainText().strip()
        if not user_message:
            return

        if not self.api_key:
             QMessageBox.warning(self, "API Key Missing", "Please set your Gemini API key in Preferences first.")
             return

        self._append_message("You", user_message, "user")
        self.user_input.clear()
        self.send_button.setEnabled(False)
        self.send_button.setText("Thinking...")

        # Prepare prompt with context and history
        full_prompt = self._build_full_prompt(user_message)

        # Start AI processing in a separate thread
        self.ai_thread = AIThread(self.api_key, full_prompt)
        self.ai_thread.result_ready.connect(self.on_ai_response)
        self.ai_thread.error_occurred.connect(self.on_ai_error)
        self.ai_thread.finished.connect(lambda: (self.send_button.setEnabled(True), self.send_button.setText("Send")))
        self.ai_thread.start()

    def _build_full_prompt(self, current_message):
        """Builds the full prompt including context and history."""
        prompt_parts = []
        # Add initial context (without timestamp)
        prompt_parts.append(self._generate_initial_context())
        prompt_parts.append("\n--- Conversation History ---\n")
        # Add previous conversation turns (limit to last N for token management?)
        for msg in self.chat_history:
            if msg['type'] in ['user', 'ai']:
                prompt_parts.append(f"{msg['sender']}: {msg['message']}")
        # Add the latest user message
        prompt_parts.append(f"You: {current_message}")
        prompt_parts.append("\nAI: ")
        return "\n".join(prompt_parts)

    def on_ai_response(self, response):
        """Handle AI response."""
        self._append_message("Gemini", response, "ai")

    def on_ai_error(self, error_message):
        """Handle AI error."""
        self._append_message("System", f"Error: {error_message}", "error")

    def closeEvent(self, event):
        """Save window geometry on close."""
        self.settings.setValue("ai_chat_geometry", self.saveGeometry())
        super().closeEvent(event)
# --- YENI SINIF SONU ---


class MedicalImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏥 Enhanced Medical Imaging Viewer")
        self.setGeometry(100, 100, 1400, 900)

        # Settings
        self.settings = QSettings("MedicalViewer", "EnhancedViewer")

        # Data variables
        self.image_data = None
        self.pixel_array = None
        self.current_slice = 0
        self.modality = "CT"
        self.is_3d = False
        self.patient_info = {}
        self.image_info = {}

        # Image processing parameters
        self.window_center = 40
        self.window_width = 80
        self.brightness = 0
        self.contrast = 100

        # Theme settings
        self.dark_mode = self.settings.value("dark_mode", False, type=bool)

        # AI settings
        self.gemini_api_key = self.settings.value("gemini_api_key", "", type=str)
        self.ai_report = ""

        # Extended presets
        self.presets = {
            'CT': {
                'Brain': (40, 80),
                'Bone': (400, 1800),
                'Lung': (-600, 1600),
                'Soft Tissue': (50, 400),
                'Subdural': (75, 150),
                'Stroke': (35, 40),
                'Liver': (60, 160),
                'Mediastinum': (50, 350),
                'Abdomen': (40, 400),
                'Chest': (40, 700),
                'Spine': (300, 2000)
            },
            'MRI': {
                'T1 Brain': (400, 800),
                'T2 Brain': (100, 200),
                'FLAIR': (70, 200),
                'T1 Spine': (300, 800),
                'T2 Spine': (120, 250),
                'Prostate': (200, 400),
                'Breast': (150, 300)
            },
            'US': {
                'General': (128, 255),
                'Cardiac': (100, 200),
                'Abdominal': (128, 255),
                'Vascular': (100, 200),
                'Obstetric': (128, 255)
            },
            'MG': {
                'Breast': (1000, 3000),
                'Calcification': (2000, 4000),
                'Mass': (1500, 3000)
            }
        }

        self.modality_names = {
            'CT': 'Computed Tomography',
            'MRI': 'Magnetic Resonance Imaging',
            'US': 'Ultrasound',
            'MG': 'Mammography'
        }

        # Apply theme
        self.apply_theme()

        # Create UI
        self.create_ui()
        self.create_menu()
        self.create_status_bar()

        # Generate sample data
        self.generate_sample_data()
        self.update_image()

        # --- YENI: AI Chat dialog referansı ---
        self._current_chat_dialog = None # AI Chat dialog referansı için

    def apply_theme(self):
        """Apply dark or light theme"""
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    border-radius: 5px;
                    margin-top: 1ex;
                    font-weight: bold;
                    color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 5px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #4c4c4c;
                }
                QPushButton:pressed {
                    background-color: #2c2c2c;
                }
                QComboBox, QSlider, QLineEdit {
                    background-color: #3c3c3c;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    color: #ffffff;
                }
                QScrollBar:vertical {
                    background: #3c3c3c;
                    width: 15px;
                    margin: 22px 0 22px 0;
                }
                QScrollBar::handle:vertical {
                    background: #555555;
                    border-radius: 4px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    margin-top: 1ex;
                    font-weight: bold;
                }
            """)

    def create_ui(self):
        """Create the main UI"""
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Main layout
        main_layout = QVBoxLayout(main_widget)

        # Header with theme toggle
        header_layout = QHBoxLayout()

        self.image_info_label = QLabel("CT Brain Image - WC: 40 | WW: 80")
        self.image_info_label.setAlignment(Qt.AlignLeft)
        self.image_info_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.image_info_label)

        header_layout.addStretch()

        # Theme toggle buttons
        self.light_theme_btn = QPushButton("☀️ Light")
        self.light_theme_btn.setCheckable(True)
        self.light_theme_btn.clicked.connect(lambda: self.toggle_theme(False))
        header_layout.addWidget(self.light_theme_btn)

        self.dark_theme_btn = QPushButton("🌙 Dark")
        self.dark_theme_btn.setCheckable(True)
        self.dark_theme_btn.clicked.connect(lambda: self.toggle_theme(True))
        header_layout.addWidget(self.dark_theme_btn)

        # Set initial theme button states
        if self.dark_mode:
            self.dark_theme_btn.setChecked(True)
        else:
            self.light_theme_btn.setChecked(True)

        main_layout.addLayout(header_layout)

        # Splitter for resizable panels
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        # Left panel - Image display
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Matplotlib figure
        self.figure = Figure(figsize=(10, 8), facecolor='black' if self.dark_mode else 'white')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('black' if self.dark_mode else 'white')
        left_layout.addWidget(self.canvas)

        self.splitter.addWidget(left_widget)

        # Right panel - Controls
        self.create_controls_panel(self.splitter)

        # Set initial sizes
        self.splitter.setSizes([900, 300])

    def create_controls_panel(self, parent):
        """Create controls panel"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)

        # File operations
        file_group = QGroupBox("📁 File Operations")
        file_layout = QVBoxLayout(file_group)

        load_btn = QPushButton("📂 Load Medical File (DICOM/NIFTI)")
        load_btn.clicked.connect(self.load_medical_file)
        file_layout.addWidget(load_btn)

        self.report_btn = QPushButton("📝 Create Patient Report")
        self.report_btn.clicked.connect(self.create_patient_report)
        file_layout.addWidget(self.report_btn)
        self.report_btn.setEnabled(False)

        scroll_layout.addWidget(file_group)

        # Modality selection
        modality_group = QGroupBox("🩺 Modality")
        modality_layout = QVBoxLayout(modality_group)

        self.modality_combo = QComboBox()
        self.modality_combo.addItems(list(self.modality_names.keys()))
        self.modality_combo.setCurrentText("CT")
        self.modality_combo.currentTextChanged.connect(self.on_modality_change)
        modality_layout.addWidget(self.modality_combo)

        scroll_layout.addWidget(modality_group)

        # Presets
        preset_group = QGroupBox("🔧 Windowing Presets")
        preset_layout = QVBoxLayout(preset_group)

        self.preset_combo = QComboBox()
        self.update_preset_list()
        self.preset_combo.currentTextChanged.connect(self.on_preset_change)
        preset_layout.addWidget(self.preset_combo)

        scroll_layout.addWidget(preset_group)

        # Manual windowing
        windowing_group = QGroupBox("🎚️ Manual Windowing")
        windowing_layout = QFormLayout(windowing_group)
        windowing_layout.setSpacing(10)

        # Window Center
        self.wc_slider = QSlider(Qt.Horizontal)
        self.wc_slider.setRange(-2000, 2000)
        self.wc_slider.setValue(self.window_center)
        self.wc_slider.valueChanged.connect(self.on_wc_change)
        self.wc_label = QLabel(str(self.window_center))
        windowing_layout.addRow("Window Center:", self.wc_slider)
        windowing_layout.addRow("", self.wc_label)

        # Window Width
        self.ww_slider = QSlider(Qt.Horizontal)
        self.ww_slider.setRange(1, 4000)
        self.ww_slider.setValue(self.window_width)
        self.ww_slider.valueChanged.connect(self.on_ww_change)
        self.ww_label = QLabel(str(self.window_width))
        windowing_layout.addRow("Window Width:", self.ww_slider)
        windowing_layout.addRow("", self.ww_label)

        scroll_layout.addWidget(windowing_group)

        # Brightness & Contrast
        bc_group = QGroupBox("🌟 Brightness & Contrast")
        bc_layout = QFormLayout(bc_group)
        bc_layout.setSpacing(10)

        # Brightness
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(self.brightness)
        self.brightness_slider.valueChanged.connect(self.on_brightness_change)
        self.brightness_label = QLabel(str(self.brightness))
        bc_layout.addRow("Brightness:", self.brightness_slider)
        bc_layout.addRow("", self.brightness_label)

        # Contrast
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(10, 300)
        self.contrast_slider.setValue(self.contrast)
        self.contrast_slider.valueChanged.connect(self.on_contrast_change)
        self.contrast_label = QLabel(f"{self.contrast}%")
        bc_layout.addRow("Contrast:", self.contrast_slider)
        bc_layout.addRow("", self.contrast_label)

        scroll_layout.addWidget(bc_group)

        # Slice navigation
        self.slice_group = QGroupBox("🧊 Slice Navigation")
        slice_layout = QVBoxLayout(self.slice_group)

        self.slice_label = QLabel("Slice: 1 / 1")
        slice_layout.addWidget(self.slice_label)

        self.slice_slider = QSlider(Qt.Horizontal)
        self.slice_slider.setRange(0, 0)
        self.slice_slider.valueChanged.connect(self.on_slice_change)
        slice_layout.addWidget(self.slice_slider)

        scroll_layout.addWidget(self.slice_group)
        self.slice_group.setVisible(False)

        # AI Assistant
        ai_group = QGroupBox("🤖 AI Assistant (Gemini)")
        ai_layout = QVBoxLayout(ai_group)

        ai_btn_layout = QHBoxLayout()
        self.set_api_btn = QPushButton("🔑 Set API Key")
        self.set_api_btn.clicked.connect(self.set_api_key)
        ai_btn_layout.addWidget(self.set_api_btn)

        self.generate_report_btn = QPushButton("📝 Generate AI Report")
        self.generate_report_btn.clicked.connect(self.generate_ai_report)
        ai_btn_layout.addWidget(self.generate_report_btn)

        self.view_report_btn = QPushButton("👁️ View Report")
        self.view_report_btn.clicked.connect(self.view_ai_report)
        ai_btn_layout.addWidget(self.view_report_btn)

        ai_layout.addLayout(ai_btn_layout)
        scroll_layout.addWidget(ai_group)

        # Reset button
        reset_btn = QPushButton("🔄 Reset All Values")
        reset_btn.clicked.connect(self.reset_values)
        scroll_layout.addWidget(reset_btn)

        scroll_area.setWidget(scroll_widget)
        parent.addWidget(scroll_area)

    def create_menu(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        load_action = QAction("📂 Load Medical File", self)
        load_action.triggered.connect(self.load_medical_file)
        file_menu.addAction(load_action)

        report_action = QAction("📝 Create Patient Report", self)
        report_action.triggered.connect(self.create_patient_report)
        report_action.setEnabled(False)
        file_menu.addAction(report_action)
        self.report_menu_action = report_action

        file_menu.addSeparator()

        preferences_action = QAction("⚙️ Preferences", self)
        preferences_action.triggered.connect(self.show_preferences)
        file_menu.addAction(preferences_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("View")

        reset_action = QAction("🔄 Reset Values", self)
        reset_action.triggered.connect(self.reset_values)
        view_menu.addAction(reset_action)

        fullscreen_action = QAction("🖥️ Full Screen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # AI menu
        ai_menu = menubar.addMenu("AI")

        set_key_action = QAction("🔑 Set API Key", self)
        set_key_action.triggered.connect(self.set_api_key)
        ai_menu.addAction(set_key_action)

        generate_action = QAction("📝 Generate Report", self)
        generate_action.triggered.connect(self.generate_ai_report)
        ai_menu.addAction(generate_action)

        view_action = QAction("👁️ View Report", self)
        view_action.triggered.connect(self.view_ai_report)
        ai_menu.addAction(view_action)

        # --- YENI: AI Chat menü öğesi ---
        chat_action = QAction("💬 AI Chat", self)
        chat_action.triggered.connect(self.open_ai_chat)
        ai_menu.addAction(chat_action)
        # --- YENI SON ---

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Enhanced Medical Imaging Viewer")

    def toggle_theme(self, dark_mode):
        """Toggle between dark and light theme"""
        self.dark_mode = dark_mode
        self.settings.setValue("dark_mode", dark_mode)
        self.apply_theme()

        # Update matplotlib figure colors
        self.figure.set_facecolor('black' if self.dark_mode else 'white')
        self.ax.set_facecolor('black' if self.dark_mode else 'white')
        self.update_image()

        # Update button states
        self.light_theme_btn.setChecked(not dark_mode)
        self.dark_theme_btn.setChecked(dark_mode)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def show_preferences(self):
        """Show preferences dialog"""
        prefs_dialog = QDialog(self)
        prefs_dialog.setWindowTitle("Preferences")
        prefs_dialog.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout(prefs_dialog)

        # API Key
        api_group = QGroupBox("API Settings")
        api_layout = QFormLayout(api_group)

        self.api_key_edit = QLineEdit(self.gemini_api_key)
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        api_layout.addRow("Gemini API Key:", self.api_key_edit)

        layout.addWidget(api_group)

        # Theme
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)

        self.dark_mode_check = QCheckBox("Dark Mode")
        self.dark_mode_check.setChecked(self.dark_mode)
        theme_layout.addWidget(self.dark_mode_check)

        layout.addWidget(theme_group)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_preferences(prefs_dialog))
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(prefs_dialog.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        prefs_dialog.exec_()

    def save_preferences(self, dialog):
        """Save preferences"""
        self.gemini_api_key = self.api_key_edit.text()
        self.settings.setValue("gemini_api_key", self.gemini_api_key)

        new_dark_mode = self.dark_mode_check.isChecked()
        if new_dark_mode != self.dark_mode:
            self.toggle_theme(new_dark_mode)

        dialog.accept()

    def update_preset_list(self):
        """Update preset list based on current modality"""
        modality = self.modality_combo.currentText()
        if modality in self.presets:
            preset_list = list(self.presets[modality].keys())
            self.preset_combo.clear()
            self.preset_combo.addItems(preset_list)
            if preset_list:
                self.preset_combo.setCurrentIndex(0)

    def on_modality_change(self):
        """Handle modality change"""
        self.modality = self.modality_combo.currentText()
        self.update_preset_list()
        self.update_image()

    def on_preset_change(self):
        """Handle preset change"""
        modality = self.modality_combo.currentText()
        preset_name = self.preset_combo.currentText()
        if modality in self.presets and preset_name in self.presets[modality]:
            center, width = self.presets[modality][preset_name]
            self.window_center = center
            self.window_width = width
            self.wc_slider.setValue(int(center))
            self.ww_slider.setValue(int(width))
            self.update_image()

    def on_wc_change(self, value):
        """Handle window center change"""
        self.window_center = value
        self.wc_label.setText(str(value))
        self.update_image()

    def on_ww_change(self, value):
        """Handle window width change"""
        self.window_width = value
        self.ww_label.setText(str(value))
        self.update_image()

    def on_brightness_change(self, value):
        """Handle brightness change"""
        self.brightness = value
        self.brightness_label.setText(str(value))
        self.update_image()

    def on_contrast_change(self, value):
        """Handle contrast change"""
        self.contrast = value
        self.contrast_label.setText(f"{value}%")
        self.update_image()

    def on_slice_change(self, value):
        """Handle slice change"""
        self.current_slice = value
        self.update_slice_label()
        self.update_image()

    def update_slice_label(self):
        """Update slice navigation label"""
        if self.is_3d and self.pixel_array is not None:
            if len(self.pixel_array.shape) >= 3:
                if len(self.pixel_array.shape) == 3:
                    total = self.pixel_array.shape[2] if self.pixel_array.shape[2] > 0 else 1
                else:
                    total = self.pixel_array.shape[0] if self.pixel_array.shape[0] > 0 else 1
            else:
                total = self.pixel_array.shape[0] if self.pixel_array.shape[0] > 0 else 1
            self.slice_label.setText(f"Slice: {self.current_slice + 1} / {total}")

    def generate_sample_data(self, modality="CT", slices=1):
        """Generate sample medical data"""
        width, height = 512, 512

        if slices == 1:
            data = np.zeros((height, width), dtype=np.float32)
            self.is_3d = False
        else:
            data = np.zeros((slices, height, width), dtype=np.float32)
            self.is_3d = True

        # Generate CT-like data
        for s in range(slices):
            if slices == 1:
                slice_data = data
            else:
                slice_data = data[s]

            for y in range(height):
                for x in range(width):
                    center_x, center_y = width // 2, height // 2
                    distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)

                    # Brain tissue simulation
                    if distance < 200:
                        value = 1064 + np.random.random() * 40
                        if distance < 120:
                            value = 1054 + np.random.random() * 30
                        if distance < 80 and np.random.random() > 0.7:
                            value = 1039 + np.random.random() * 10
                        if np.random.random() > 0.95:
                            value = 1074 + np.random.random() * 20
                    elif distance < 220:
                        value = 2024 + np.random.random() * 200
                    else:
                        value = 24 + np.random.random() * 10

                    slice_data[y, x] = value

        # Convert to uint16 safely
        self.pixel_array = np.clip(data, 0, 4095).astype(np.uint16)
        self.modality = modality
        self.modality_combo.setCurrentText(modality)
        self.current_slice = slices // 2 if slices > 1 else 0

        # Update patient info
        self.patient_info = {
            'name': 'Sample Patient',
            'id': 'SAMPLE001',
            'date': '2024-01-15',
            'modality': modality
        }

        self.image_info = {
            'description': f'Sample {modality} Image',
            'wc': self.window_center,
            'ww': self.window_width
        }

        # Update controls
        if self.is_3d:
            self.slice_slider.setRange(0, max(0, slices-1))
            self.slice_slider.setValue(self.current_slice)
            self.slice_group.setVisible(True)
            self.update_slice_label()
        else:
            self.slice_group.setVisible(False)

        self.update_preset_list()
        self.report_btn.setEnabled(True)
        self.report_menu_action.setEnabled(True)

    def load_medical_file(self):
        """Load medical file (DICOM or NIFTI)"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Medical Image File",
            "", "Medical files (*.dcm *.dicom *.nii *.nii.gz);;All files (*.*)"
        )

        if filename:
            try:
                if filename.endswith(('.nii', '.nii.gz')):
                    self.load_nifti_file(filename)
                else:
                    self.load_dicom_file(filename)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading file:\n{str(e)}")

    def load_dicom_file(self, filename):
        """Load DICOM file"""
        if not PYDICOM_AVAILABLE:
            QMessageBox.critical(self, "Error", "pydicom not installed!\n\nRun: pip install pydicom")
            return

        try:
            self.metadata = pydicom.dcmread(filename)

            # Convert pixel array to float32
            raw_pixel_array = self.metadata.pixel_array
            if raw_pixel_array.dtype == np.uint16:
                self.pixel_array = raw_pixel_array.astype(np.float32)
            else:
                self.pixel_array = raw_pixel_array.astype(np.float32)

            # Check if 3D
            self.is_3d = len(self.pixel_array.shape) == 3
            self.modality = getattr(self.metadata, 'Modality', 'CT')

            # Update patient info from DICOM
            self.patient_info = {
                'name': str(getattr(self.metadata, 'PatientName', 'Unknown')),
                'id': str(getattr(self.metadata, 'PatientID', 'Unknown')),
                'date': str(getattr(self.metadata, 'StudyDate', 'Unknown')),
                'modality': self.modality
            }

            # Update image info
            self.image_info = {
                'description': str(getattr(self.metadata, 'StudyDescription', 'Unknown')),
                'wc': self.window_center,
                'ww': self.window_width
            }

            if self.is_3d:
                self.current_slice = self.pixel_array.shape[0] // 2
                self.slice_slider.setRange(0, max(0, self.pixel_array.shape[0]-1))
                self.slice_slider.setValue(self.current_slice)
                self.slice_group.setVisible(True)
                self.update_slice_label()
            else:
                self.slice_group.setVisible(False)

            # Update windowing from DICOM
            try:
                wc = getattr(self.metadata, 'WindowCenter', None)
                ww = getattr(self.metadata, 'WindowWidth', None)

                if wc is not None:
                    if hasattr(wc, '__iter__') and not isinstance(wc, str):
                        self.window_center = float(wc[0])
                    else:
                        self.window_center = float(wc)
                    self.wc_slider.setValue(int(self.window_center))

                if ww is not None:
                    if hasattr(ww, '__iter__') and not isinstance(ww, str):
                        self.window_width = float(ww[0])
                    else:
                        self.window_width = float(ww)
                    self.ww_slider.setValue(int(self.window_width))
            except Exception as e:
                print(f"Could not read DICOM windowing: {e}")

            self.modality_combo.setCurrentText(self.modality)
            self.update_preset_list()
            self.update_image()

            patient_name = getattr(self.metadata, 'PatientName', 'Unknown')
            QMessageBox.information(self, "Success", f"DICOM file loaded successfully!\n\nPatient: {patient_name}\nDimensions: {raw_pixel_array.shape}")

            # Enable report button
            self.report_btn.setEnabled(True)
            self.report_menu_action.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading DICOM file:\n{str(e)}")

    def load_nifti_file(self, filename):
        """Load NIFTI file"""
        if not NIBABEL_AVAILABLE:
            QMessageBox.critical(self, "Error", "nibabel not installed!\n\nRun: pip install nibabel")
            return

        try:
            nifti_img = nib.load(filename)
            self.pixel_array = nifti_img.get_fdata()

            # Handle different data types
            if self.pixel_array.dtype != np.float32:
                self.pixel_array = self.pixel_array.astype(np.float32)

            # Check if 3D or 4D
            if len(self.pixel_array.shape) >= 3:
                self.is_3d = True
                if len(self.pixel_array.shape) == 4:
                    # Take first volume if 4D
                    self.pixel_array = self.pixel_array[:, :, :, 0]
                self.current_slice = self.pixel_array.shape[2] // 2
                self.slice_slider.setRange(0, max(0, self.pixel_array.shape[2]-1))
                self.slice_slider.setValue(self.current_slice)
                self.slice_group.setVisible(True)
                self.update_slice_label()
            else:
                self.is_3d = False
                self.slice_group.setVisible(False)

            self.modality = "MRI"  # Assume MRI for NIFTI
            self.modality_combo.setCurrentText(self.modality)

            # Update patient info
            self.patient_info = {
                'name': 'NIFTI Patient',
                'id': 'NIFTI001',
                'date': '2024-01-15',
                'modality': self.modality
            }

            self.image_info = {
                'description': 'NIFTI Image',
                'wc': self.window_center,
                'ww': self.window_width
            }

            self.update_preset_list()
            self.update_image()

            QMessageBox.information(self, "Success", f"NIFTI file loaded successfully!\n\nDimensions: {self.pixel_array.shape}")

            # Enable report button
            self.report_btn.setEnabled(True)
            self.report_menu_action.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading NIFTI file:\n{str(e)}")

    def apply_dicom_windowing(self, image, center, width, rescale_slope=1.0, rescale_intercept=-1024.0):
        """Apply DICOM windowing with VOI LUT formula"""
        try:
            # Ensure we're working with float arrays
            if image.dtype != np.float32 and image.dtype != np.float64:
                image = image.astype(np.float32)

            # Convert to actual values
            rescale_slope = float(rescale_slope)
            rescale_intercept = float(rescale_intercept)

            x = image * rescale_slope + rescale_intercept

            # DICOM VOI LUT standard formula
            ymin, ymax = 0.0, 255.0
            c, w = float(center), float(width)

            # Apply windowing formula
            lower_bound = c - 0.5 - (w - 1) / 2
            upper_bound = c - 0.5 + (w - 1) / 2

            # Vectorized windowing calculation
            y = np.zeros_like(x, dtype=np.float32)

            # Apply conditions
            below_mask = x <= lower_bound
            above_mask = x > upper_bound
            between_mask = ~below_mask & ~above_mask

            y[below_mask] = ymin
            y[above_mask] = ymax
            y[between_mask] = ((x[between_mask] - (c - 0.5)) / (w - 1) + 0.5) * (ymax - ymin) + ymin

            # Ensure output is in valid range and convert to uint8
            result = np.clip(y, ymin, ymax).astype(np.uint8)

            return result

        except Exception as e:
            print(f"Error in windowing: {e}")
            # Fallback: simple min-max scaling
            normalized = (image - image.min()) / (image.max() - image.min())
            return (normalized * 255).astype(np.uint8)

    def apply_brightness_contrast(self, image, brightness, contrast):
        """Apply brightness and contrast adjustments"""
        try:
            # Ensure image is float for calculations
            img_float = image.astype(np.float32)
            contrast_factor = contrast / 100.0

            # Apply contrast around midpoint, then brightness
            adjusted = ((img_float - 128.0) * contrast_factor) + 128.0 + brightness

            # Clip and convert back to uint8
            return np.clip(adjusted, 0, 255).astype(np.uint8)
        except Exception as e:
            print(f"Error in brightness/contrast: {e}")
            return image

    def get_current_slice(self):
        """Get current slice data"""
        if self.pixel_array is None:
            return None

        if self.is_3d:
            if len(self.pixel_array.shape) == 3:
                return self.pixel_array[:, :, self.current_slice]
            else:
                return self.pixel_array[self.current_slice]
        else:
            return self.pixel_array

    def process_image(self):
        """Process the current image with all enhancements"""
        slice_data = self.get_current_slice()
        if slice_data is None:
            return None

        try:
            # Get parameters
            center = self.window_center
            width = self.window_width

            # Default values if metadata not available
            rescale_slope = getattr(getattr(self, 'metadata', None), 'RescaleSlope', 1.0) if hasattr(self, 'metadata') else 1.0
            rescale_intercept = getattr(getattr(self, 'metadata', None), 'RescaleIntercept', -1024.0) if hasattr(self, 'metadata') else -1024.0

            # Apply windowing
            processed = self.apply_dicom_windowing(slice_data, center, width, rescale_slope, rescale_intercept)

            # Apply brightness and contrast
            final = self.apply_brightness_contrast(processed, self.brightness, self.contrast)

            return final

        except Exception as e:
            print(f"Error processing image: {e}")
            # Return a simple normalized version as fallback
            normalized = (slice_data - slice_data.min()) / (slice_data.max() - slice_data.min())
            return (normalized * 255).astype(np.uint8)

    def update_image(self):
        """Update the displayed image"""
        try:
            processed_image = self.process_image()
            if processed_image is None:
                return

            # Clear and update plot
            self.ax.clear()
            self.ax.imshow(processed_image, cmap='gray', vmin=0, vmax=255)
            self.ax.set_title(f"{self.modality_names.get(self.modality, self.modality)} Image", color='white' if self.dark_mode else 'black', fontsize=12)
            self.ax.axis('off')

            # Update canvas
            self.canvas.draw()

            # Update info label
            self.image_info_label.setText(f"{self.modality_names.get(self.modality, self.modality)} Image - WC: {int(self.window_center)} | WW: {int(self.window_width)}")

            # Update status bar
            self.status_bar.showMessage(f"Displaying {self.modality} image - Window Center: {int(self.window_center)}, Window Width: {int(self.window_width)}")

            # Update image info
            self.image_info['wc'] = int(self.window_center)
            self.image_info['ww'] = int(self.window_width)

        except Exception as e:
            print(f"Error updating image: {e}")

    def reset_values(self):
        """Reset all values to defaults"""
        self.window_center = 40
        self.window_width = 80
        self.brightness = 0
        self.contrast = 100

        self.wc_slider.setValue(40)
        self.ww_slider.setValue(80)
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(100)

        self.modality_combo.setCurrentText("CT")
        self.modality = "CT"

        if self.is_3d:
            self.slice_slider.setValue(0)
            self.current_slice = 0

        self.update_preset_list()
        self.update_image()

    def set_api_key(self):
        """Set Gemini API key"""
        api_key, ok = QInputDialog.getText(self, "API Key", "Enter Gemini API Key:", QLineEdit.Password)
        if ok:
            self.gemini_api_key = api_key
            self.settings.setValue("gemini_api_key", api_key)
            QMessageBox.information(self, "Success", "API key saved successfully!")

    def generate_ai_report(self):
        """Generate AI report using Gemini API"""
        if not self.gemini_api_key:
            QMessageBox.warning(self, "Error", "Please set Gemini API key first!")
            return

        try:
            # Get current image info for context
            modality = self.modality_names.get(self.modality, self.modality)
            preset = self.preset_combo.currentText()

            prompt = f"""
            You are a medical imaging expert. Analyze this {modality} image with {preset} windowing.
            Provide a professional medical report including:

            1. Image Quality Assessment
            2. Technical Parameters Used
            3. Key Findings
            4. Clinical Implications
            5. Recommendations

            Keep the report professional and concise.
            """

            # Show processing message
            self.status_bar.showMessage("Generating AI report...")

            # Create and start AI thread
            self.ai_thread = AIThread(self.gemini_api_key, prompt)
            self.ai_thread.result_ready.connect(self.on_ai_result)
            self.ai_thread.error_occurred.connect(self.on_ai_error)
            self.ai_thread.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating AI report:\n{str(e)}")

    def on_ai_result(self, result):
        """Handle AI result"""
        self.ai_report = result
        self.status_bar.showMessage("AI report generated successfully!")
        QMessageBox.information(self, "Success", "AI report generated successfully!")

    def on_ai_error(self, error):
        """Handle AI error"""
        self.status_bar.showMessage("Error generating AI report")
        QMessageBox.critical(self, "AI Error", error)

    def view_ai_report(self):
        """View AI report"""
        if not self.ai_report:
            QMessageBox.information(self, "Info", "No AI report generated yet!")
            return

        # Create report window
        report_window = QMainWindow()
        report_window.setWindowTitle("AI Medical Report")
        report_window.setGeometry(200, 200, 800, 600)

        text_edit = QTextEdit()
        text_edit.setPlainText(self.ai_report)
        text_edit.setReadOnly(True)
        report_window.setCentralWidget(text_edit)

        report_window.show()

    def create_patient_report(self):
        """Create patient report dialog"""
        dialog = PatientReportDialog(self.patient_info, self.image_info, self)
        if dialog.exec_() == QDialog.Accepted:
            report_data = dialog.get_report_data()
            QMessageBox.information(self, "Success", "Patient report saved successfully!")

    # --- YENI METOD: open_ai_chat ---
    def open_ai_chat(self):
        """Open the AI chat dialog."""
        if not self.gemini_api_key:
            QMessageBox.warning(self, "API Key Missing", "Please set your Gemini API key in Preferences (File -> Preferences) first.")
            return

        dialog = AIChatDialog(self.patient_info, self.image_info, self.gemini_api_key, self)
        # Dialog modal olmasin, boylece ana pencereyle etkilesim kurmaya devam edebilirsiniz.
        dialog.setModal(False)
        dialog.show()
        # Pencerenin kapanmamasi icin referans tutulmasi gerekebilir (PyQt bazen referansi kaybedebilir)
        # Basit bir cozum: dialog'u bir instance degiskeninde saklamak
        # Ancak birden fazla chat penceresi acilmasini istiyorsaniz, bir liste tutmak gerekir.
        # Burada sadece son acilanı takip edelim:
        self._current_chat_dialog = dialog # Referansı tut
    # --- YENI METOD SON ---

    def show_about(self):
        """Show about dialog"""
        QMessageBox.information(self, "About",
            "🏥 Enhanced Medical Imaging Viewer\n\n"
            "Professional medical image processing tool\n\n"
            "Features:\n"
            "• DICOM & NIFTI support\n"
            "• Multi-modality imaging\n"
            "• Advanced windowing presets\n"
            "• AI report generation (Gemini)\n"
            "• 3D volume navigation\n"
            "• Interactive windowing\n"
            "• Dark/Light theme\n"
            "• Patient reporting system")


def main():
    """Main function"""
    print("🏥 Starting Enhanced Medical Imaging Viewer...")

    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Medical Imaging Viewer")

    viewer = MedicalImageViewer()
    viewer.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
