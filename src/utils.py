import json
import hashlib
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
import keyring
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class PasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AIrab Security")
        self.setFixedSize(300, 120)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter password for secure storage:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
        self.setLayout(layout)

def load_or_create_key():
    """Load or create encryption key using keyring"""
    service = "AIrab"
    key_str = keyring.get_password(service, "app_key")
    if not key_str:
        dlg = PasswordDialog()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            key = Fernet.generate_key()
            keyring.set_password(service, "app_key", key.decode())
            return key
        else:
            raise ValueError("Password required")
    return Fernet.generate_key()  # For now; later use stored key

def hash_filename(fname: str) -> str:
    """Generate hashed filename for obfuscation"""
    timestamp = str(datetime.now().timestamp())
    h = hashlib.sha256((fname + timestamp).encode()).hexdigest()[:16]
    return f"{h}.{Path(fname).suffix}"

def save_chats(chats: dict, data_dir: Path):
    """Save chat history to JSON"""
    json.dump(chats, open(data_dir / "history.json", 'w'), indent=2)

def load_chats(data_dir: Path) -> dict:
    """Load chat history from JSON"""
    hist_file = data_dir / "history.json"
    return json.load(open(hist_file)) if hist_file.exists() else {}
