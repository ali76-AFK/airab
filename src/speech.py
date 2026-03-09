from PyQt6.QtCore import QThread, pyqtSignal

class SpeechToText(QThread):
    text_ready = pyqtSignal(str)
    
    def run(self):
        # SAFE MOCK - no audio devices, no crashes
        self.text_ready.emit("🎤 Speech working!")

class TextToSpeech(QThread):
    def __init__(self, text):
        super().__init__()
        self.text = text
        
    def run(self):
        pass  # Silent mock TTS
