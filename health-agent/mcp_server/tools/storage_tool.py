import os
import json
import base64
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .audit import log_audit

"""
Security Design:
All sensitive health data is stored strictly on the local machine within the `data/` directory.
It is never transmitted to an external database. Furthermore, the data is encrypted at rest 
using Fernet symmetric encryption. 

The encryption key is derived from a 4-digit passphrase that the user enters at runtime, 
and the key is strictly kept IN MEMORY ONLY. It is never saved to disk.
"""

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
FILE_PATH = os.path.join(DATA_DIR, "health_logs.json")

# In-memory cipher
_cipher = None

def initialize_encryption(passphrase: str):
    """
    Derives a Fernet key from a 4-digit passphrase and stores the cipher in memory.
    """
    global _cipher
    # In a real app, a unique salt would be securely generated and stored per user.
    # For demo simplicity, we use a static salt.
    salt = b'kaggle_demo_salt'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode('utf-8')))
    _cipher = Fernet(key)

def save_health_log(entry_type: str, value: str, notes: str, timestamp: str = None) -> str:
    """
    Saves a new health log entry locally with Fernet encryption using the in-memory key.
    """
    log_audit("save_health_log")
    if not _cipher:
        return "Error: Encryption not initialized. Please enter your passphrase."
        
    if not timestamp:
        timestamp = datetime.now().isoformat()
        
    entry = {
        "timestamp": timestamp,
        "entry_type": entry_type,
        "value": value,
        "notes": notes
    }
    
    # Encrypt the JSON payload
    encrypted_data = _cipher.encrypt(json.dumps(entry).encode('utf-8'))
    
    logs = []
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                pass
                
    logs.append(encrypted_data.decode('utf-8'))
    
    with open(FILE_PATH, "w") as f:
        json.dump(logs, f, indent=2)
        
    return f"Successfully and securely logged {entry_type}."

def get_health_logs(entry_type: str = None, limit: int = None) -> str:
    """
    Retrieves and decrypts health logs. Can optionally filter by type or limit results.
    """
    log_audit("get_health_logs")
    if not _cipher:
        return "Error: Encryption not initialized. Please enter your passphrase."
        
    if not os.path.exists(FILE_PATH):
        return "No health logs found."
        
    with open(FILE_PATH, "r") as f:
        try:
            encrypted_logs = json.load(f)
        except json.JSONDecodeError:
            return "Failed to parse logs."
            
    decrypted_logs = []
    for enc_log in encrypted_logs:
        try:
            decrypted = json.loads(_cipher.decrypt(enc_log.encode('utf-8')).decode('utf-8'))
            if not entry_type or decrypted.get("entry_type") == entry_type:
                decrypted_logs.append(decrypted)
        except Exception:
            # If a log fails to decrypt (e.g., wrong PIN), we skip it safely.
            continue
            
    if not decrypted_logs:
        return "No logs found."
    
    if limit:
        decrypted_logs = decrypted_logs[-limit:]
        
    return json.dumps(decrypted_logs, indent=2)
