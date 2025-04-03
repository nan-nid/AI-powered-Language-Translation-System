import sys
import speech_recognition as sr
from gtts import gTTS
import os
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox, QTextEdit
)
from PyQt5.QtGui import QFont, QPalette, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
from googletrans import Translator, LANGUAGES

class RealTimeConversation(QWidget):
    def __init__(self):
        super().__init__()
        self.running = False  # Control loop for real-time mode
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('🌍 REAL-TIME CONVERSATION TRANSLATOR 🌍')
        self.setGeometry(200, 200, 650, 550)
        self.setStyleSheet("background-color: #1e1e2e; color: #ffffff;")

        self.create_widgets()
        self.layout_widgets()
        self.connect_signals()

    def create_widgets(self):
        """Create UI Elements"""
        self.source_language_label = QLabel('👤 SPEAKER 1 LANGUAGE:')
        self.source_language_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.source_language_combo = QComboBox()
        self.source_language_combo.addItems(LANGUAGES.values())
        self.source_language_combo.setStyleSheet("background-color: #3b4252; color: #ffffff; padding: 5px; border-radius: 5px")

        self.target_language_label = QLabel('👥 SPEAKER 2 LANGUAGE:')
        self.target_language_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.target_language_combo = QComboBox()
        self.target_language_combo.addItems(LANGUAGES.values())
        self.target_language_combo.setStyleSheet("background-color: #3b4252; color: #ffffff; padding: 5px; border-radius: 5px")

        # Speech Accent Selection
        self.accent_label = QLabel('🎤 CHOOSE ACCENT:')
        self.accent_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.accent_combo = QComboBox()
        self.accent_combo.addItems(["Default", "English (US)", "English (UK)", "English (Australia)", "English (India)"])
        self.accent_combo.setStyleSheet("background-color: #3b4252; color: #ffffff; padding: 5px; border-radius: 5px")

        # Conversation Box with Auto-Scroll
        self.conversation_box = QTextEdit()
        self.conversation_box.setFont(QFont('Arial', 12))
        self.conversation_box.setReadOnly(True)
        self.conversation_box.setPlaceholderText("Conversation will appear here...")
        self.conversation_box.setStyleSheet("background-color: #2e3440; color: #ffffff; padding: 10px; border-radius: 5px")

        # Buttons
        self.start_button = QPushButton('🎤 START CONVERSATION')
        self.stop_button = QPushButton('⏹ STOP')

        for btn in [self.start_button, self.stop_button]:
            btn.setFont(QFont('Arial', 12, QFont.Bold))
            btn.setStyleSheet("background-color: #4c566a; color: #ffffff; padding: 8px; border-radius: 5px")

    def layout_widgets(self):
        """Arrange UI Elements"""
        layout = QVBoxLayout()
        layout.addWidget(self.source_language_label)
        layout.addWidget(self.source_language_combo)
        layout.addWidget(self.target_language_label)
        layout.addWidget(self.target_language_combo)
        layout.addWidget(self.accent_label)
        layout.addWidget(self.accent_combo)
        layout.addWidget(self.conversation_box)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

    def connect_signals(self):
        """Connect Buttons to Functions"""
        self.start_button.clicked.connect(self.start_conversation)
        self.stop_button.clicked.connect(self.stop_conversation)

    def start_conversation(self):
        """Start Continuous Speech Translation"""
        self.running = True
        threading.Thread(target=self.listen_and_translate, daemon=True).start()

    def stop_conversation(self):
        """Stop Continuous Speech Translation"""
        self.running = False

    def listen_and_translate(self):
        """Continuously Listen, Translate, and Speak"""
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        while self.running:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                try:
                    self.add_fade_in_text("🎙 Listening...")
                    audio = recognizer.listen(source, timeout=5)
                    text = recognizer.recognize_google(audio)

                    if text.strip():
                        self.add_fade_in_text(f"👤 Speaker 1: {text}")

                        # Get languages
                        src_lang = self.get_language_code(self.source_language_combo.currentText())
                        target_lang = self.get_language_code(self.target_language_combo.currentText())

                        # Translate
                        translator = Translator()
                        translated_text = translator.translate(text, src=src_lang, dest=target_lang).text
                        self.add_fade_in_text(f"👥 Speaker 2 (Translated): {translated_text}")

                        # Speak translation
                        self.speak_text(translated_text, target_lang)

                except sr.UnknownValueError:
                    self.add_fade_in_text("🤷 Could not understand audio.")
                except sr.RequestError:
                    self.add_fade_in_text("⚠️ Could not process the request. Check internet connection.")

    def speak_text(self, text, language):
        """Convert Text to Speech with Accent Options"""
        accent_mapping = {
            "English (US)": "com",
            "English (UK)": "co.uk",
            "English (Australia)": "com.au",
            "English (India)": "co.in"
        }
        accent = self.accent_combo.currentText()
        domain = accent_mapping.get(accent, None)

        try:
            tts = gTTS(text=text, lang=language, tld=domain)
            tts.save("translated_speech.mp3")
            os.system("start translated_speech.mp3")  # Works for Windows; change for Linux/Mac
        except Exception as e:
            self.add_fade_in_text(f"🔊 Speech Error: {str(e)}")

    def add_fade_in_text(self, text):
        """Adds a fade-in animation effect to new text in the conversation box"""
        self.conversation_box.append(text)
        self.conversation_box.verticalScrollBar().setValue(self.conversation_box.verticalScrollBar().maximum())

    def get_language_code(self, lang_name):
        """Convert Full Language Name to Language Code"""
        for code, name in LANGUAGES.items():
            if name.lower() == lang_name.lower():
                return code
        return "en"

def main():
    app = QApplication(sys.argv)
    translator = RealTimeConversation()
    translator.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
