"""
Audit Tool - Security Component

Provides auditing capabilities by safely logging tool executions without writing any Protected Health Information (PHI) to disk.
"""
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
AUDIT_FILE = os.path.join(DATA_DIR, "audit.log")

def log_audit(tool_name: str):
    """Appends an audit log for a tool execution (metadata only, no PHI)."""
    try:
        with open(AUDIT_FILE, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] TOOL_EXECUTION: {tool_name}\n")
    except Exception:
        pass
