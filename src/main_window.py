from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QListWidget, QTextEdit,
    QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QFileDialog, QMessageBox, QMenuBar
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QTimer

from .utils import load_or_create_key, hash_filename, save_chats, load_chats
from .speech import SpeechToText, TextToSpeech
from .llm_client import get_llm_response as mock_llm  # later replace with get_llm_response
from PyQt6.QtCore import Qt, QTimer  # Add QTimer here

class AIRabWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AIrab")
        self.setGeometry(100, 100, 1200, 800)

        # Data dir
        self.data_dir = Path.home() / "AIrab_data"
        self.data_dir.mkdir(exist_ok=True)

        # Chat state
        self.chats = {}
        self.current_chat = "default"
        self.chats[self.current_chat] = []

        # Security (password + key)
        try:
            self.key = load_or_create_key()
        except ValueError:
            # Password dialog cancelled
            return

        # UI and history
        self.init_ui()
        self.load_history()

        # Ensure at least one chat visible
        if not self.chats:
            self.chats[self.current_chat] = []
        if self.chat_list.count() == 0:
            self.chat_list.addItem(self.current_chat)

        # Theme monitoring (stub)
        self.theme_timer = QTimer()
        self.theme_timer.timeout.connect(self.apply_system_theme)
        self.theme_timer.start(1000)

    def init_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # Sidebar (chat list + buttons)
        sidebar = QWidget()
        layout = QVBoxLayout()
        self.chat_list = QListWidget()
        self.chat_list.itemClicked.connect(self.switch_chat)
        layout.addWidget(self.chat_list)

        new_btn = QPushButton("New Chat")
        new_btn.clicked.connect(self.new_chat)
        layout.addWidget(new_btn)

        clear_btn = QPushButton("Clear All Data")
        clear_btn.clicked.connect(self.clear_all)
        layout.addWidget(clear_btn)

        sidebar.setLayout(layout)
        splitter.addWidget(sidebar)

        # Main chat area
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        main_layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_box)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)

        mic_btn = QPushButton("🎤")
        mic_btn.clicked.connect(self.start_stt)
        input_layout.addWidget(mic_btn)

        file_btn = QPushButton("📎")
        file_btn.clicked.connect(self.upload_files)
        input_layout.addWidget(file_btn)

        main_layout.addLayout(input_layout)
        main_widget.setLayout(main_layout)
        splitter.addWidget(main_widget)
        splitter.setSizes([200, 1000])

        # Menus
        menubar: QMenuBar = self.menuBar()
        file_menu = menubar.addMenu("File")
        data_action = QAction("Select Data Dir", self)
        data_action.triggered.connect(self.select_data_dir)
        file_menu.addAction(data_action)

        settings_menu = menubar.addMenu("Settings")
        theme_action = QAction("Custom Theme", self)
        theme_action.triggered.connect(self.custom_theme)
        settings_menu.addAction(theme_action)

    def new_chat(self):
        chat_id = datetime.now().isoformat()[:16]  # Short ID for display
        self.chats[chat_id] = []
        self.chat_list.addItem(chat_id)
        self.current_chat = chat_id
        self.chat_display.clear()

    def switch_chat(self, item):
        cid = item.text()
        self.current_chat = cid
        if cid not in self.chats:
            self.chats[cid] = []
        self.update_display()

    def send_message(self):
        prompt = self.input_box.text().strip()
        if not prompt:
            return

        # Save user message
        self.chats[self.current_chat].append({
            "role": "user",
            "content": prompt,
            "time": datetime.now().isoformat()
        })
        self.chat_display.append(f"<b>You:</b> {prompt}")
        self.input_box.clear()

        # Call LLM
        self.process_llm(prompt)


    def process_llm(self, prompt: str):
        """FIXED: Pass file context to LLM"""
        files_text = self.get_files_text()  # ← THIS WAS MISSING!
        
        from .llm_client import get_llm_response
        response = get_llm_response(prompt, files_text)  # ← Pass files!
        
        self.chats[self.current_chat].append({
            "role": "assistant", 
            "content": response, 
            "time": datetime.now().isoformat()
        })
        self.chat_display.append(f"<b>AIrab:</b> {response}")



    def get_files_text(self) -> str:
        """FIXED: Read ALL uploaded files"""
        text = "📂 UPLOADED FILES:\n\n"
        for file in self.data_dir.glob("*"):
            if file.is_file() and file.name not in ['history.json']:
                print(f"🔍 GUI reading: {file.name}")  # Debug
                try:
                    content = file.read_text(errors='ignore')[:800]
                    text += f"📄 {file.name}:\n{content[:300]}...\n\n"
                except Exception as e:
                    text += f"❌ Error reading {file.name}: {e}\n"
        print(f"📤 Sending {len(text)} chars to AI")  # Debug
        return text[:4000]



    def upload_files(self):
        """Upload files DIRECTLY to data_dir (no hashing)"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Upload files", "", "PDF (*.pdf);;TXT (*.txt);;All (*.*)"
        )
        if len(files) > 3:
            QMessageBox.warning(self, "Limit", "Max 3 files")
            return
        
        uploaded = []
        for f in files:
            try:
                # Copy with original name to data_dir
                dest = self.data_dir / Path(f).name
                dest.write_bytes(Path(f).read_bytes())
                uploaded.append(dest.name)
                print(f"✅ Uploaded: {dest.name}")
            except Exception as e:
                print(f"❌ Upload failed: {e}")
        
        QMessageBox.information(self, "Success", f"Uploaded: {', '.join(uploaded)}")


    def start_stt(self):
        """Start speech-to-text safely."""
        try:
            if hasattr(self, "stt_thread"):
                # if a previous thread was created but finished, isRunning() may be False
                if self.stt_thread.isRunning():
                    return
            self.stt_thread = SpeechToText("vosk-model")
            self.stt_thread.text_ready.connect(self.input_box.setText)
            self.stt_thread.start()
        except Exception as e:
            self.input_box.setText(f"Speech error: {e}")

    def process_llm_simple(self, prompt):
        """SIMPLEST possible LLM - NO THREADING"""
        try:
            from .llm_client import get_llm_response
            response = get_llm_response(prompt)  # Uses mock if server fails
            self.chats[self.current_chat].append({
                "role": "assistant", "content": response, "time": datetime.now().isoformat()
            })
            self.chat_display.append(f"<b>AIrab:</b> {response}")
        except Exception as e:
            self.chat_display.append(f"<b>Error:</b> {str(e)[:100]}")


    def update_display(self):
        self.chat_display.clear()
        for msg in self.chats.get(self.current_chat, []):
            role = msg["role"].title()
            self.chat_display.append(f"<b>{role}:</b> {msg['content']}")

    def load_history(self):
        self.chats.update(load_chats(self.data_dir))
        for cid in self.chats:
            self.chat_list.addItem(cid)

    def clear_all(self):
        if QMessageBox.question(
            self, "Confirm", "Clear all data?"
        ) == QMessageBox.StandardButton.Yes:
            self.chats.clear()
            self.chat_list.clear()
            for f in self.data_dir.glob("*"):
                f.unlink(missing_ok=True)
            self.data_dir.mkdir(exist_ok=True)
            self.new_chat()

    def select_data_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        if dir_path:
            self.data_dir = Path(dir_path)

    def custom_theme(self):
        qss = """
        QMainWindow { 
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1, 
                stop:0 #f5f5dc, stop:1 #f0e68c
            ); 
        }
        QPushButton { 
            background-color: #D2B48C; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 6px; 
            font-family: 'Times New Roman';
        }
        QPushButton:hover { background-color: #c19e6f; }
        QListWidget, QTextEdit { 
            font-family: 'Times New Roman'; 
            border: 1px solid #ccc; 
            border-radius: 4px; 
            padding: 8px;
        }
        """
        self.setStyleSheet(qss)

    def apply_system_theme(self):
        # TODO: detect dark/light and adjust QSS
        pass

    def closeEvent(self, event):
        save_chats(self.chats, self.data_dir)
        event.accept()
