import os
import sys
import re
import time
import gradio as gr
from dotenv import load_dotenv

# Ensure imports resolve correctly
sys.path.append(os.path.dirname(__file__))
load_dotenv()

from google import genai
from google.genai import types

from mcp_server.tools.storage_tool import initialize_encryption, get_health_logs, save_health_log
from mcp_server.tools.reminder_tool import get_due_reminders, set_medication_reminder
from mcp_server.tools.drug_api_tool import check_drug_interaction

# --- API KEY SETUP ---
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

gemini_client = None
agent_chat = None
if api_key:
    try:
        gemini_client = genai.Client(api_key=api_key)
        agent_chat = gemini_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are a personal health concierge. You MUST use the provided tools to log health data, set medication reminders, and check drug interactions. Be extremely polite and concise. DO NOT give real medical advice without warning the user first.",
                tools=[get_health_logs, save_health_log, get_due_reminders, set_medication_reminder, check_drug_interaction]
            )
        )
        print("Gemini client initialized successfully.")
    except Exception as e:
        print(f"Failed to init Gemini client: {e}")
else:
    print("WARNING: No GEMINI_API_KEY or GOOGLE_API_KEY found.")

# --- SECURITY ---
def sanitize_input(text):
    return re.sub(r'<[^>]+>', '', text)

class RateLimiter:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def consume(self):
        now = time.time()
        self.tokens = min(self.capacity, self.tokens + (now - self.last_refill) * self.refill_rate)
        self.last_refill = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

rate_limiter = RateLimiter(capacity=20, refill_rate=20 / 60.0)
_encryption_ready = False


# --- HANDLER FUNCTIONS ---

def do_init_encryption(pin):
    """Initialize encryption and return status string."""
    global _encryption_ready
    if len(pin) != 4 or not pin.isdigit():
        return "❌ Please enter a valid 4-digit PIN."
    try:
        initialize_encryption(pin)
        _encryption_ready = True
        return "✅ Encryption initialized! You can now use the chat and sidebar."
    except Exception as e:
        return f"❌ Error: {e}"


def do_chat(message, history):
    """Chat handler for gr.ChatInterface."""
    if not _encryption_ready:
        return "🔒 Please initialize encryption first — enter your 4-digit PIN above and click Initialize."
    if not rate_limiter.consume():
        return "⚠️ Rate limit exceeded. Please wait a moment."
    clean = sanitize_input(message)
    try:
        if not agent_chat:
            return "⚠️ Gemini API key not configured. Please set GEMINI_API_KEY in your Space secrets."
        resp = agent_chat.send_message(clean)
        return resp.text
    except Exception as e:
        return f"Error: {str(e)}"


def do_refresh():
    """Fetch latest reminders and health logs for sidebar."""
    if not _encryption_ready:
        return "🔒 Initialize encryption first.", "🔒 Initialize encryption first."
    try:
        rem = get_due_reminders()
    except Exception:
        rem = "No reminders data available."
    try:
        logs = get_health_logs(limit=3)
    except Exception:
        logs = "No logs available."
    return str(rem), str(logs)


def do_export():
    """Export all logs and reminders as text."""
    if not _encryption_ready:
        return "🔒 Initialize encryption first."
    try:
        logs = get_health_logs()
        rem = get_due_reminders()
        return f"--- HEALTH SUMMARY EXPORT ---\n\nREMINDERS:\n{rem}\n\nLOGS:\n{logs}"
    except Exception as e:
        return f"Export failed: {str(e)}"


# --- BUILD THE UI ---

with gr.Blocks(theme=gr.themes.Soft(primary_hue="teal")) as demo:

    # ── HEADER ──
    gr.Markdown("# 🩺 MediGuard — Personal Health & Medication Agent")
    gr.Markdown(
        "### An AI-powered multi-agent system for medication reminders, "
        "health tracking, and drug safety checks"
    )
    gr.Markdown(
        "> **⚠️ DISCLAIMER:** This tool is not a substitute for professional "
        "medical advice. Always consult your doctor or pharmacist."
    )

    # ── PIN / ENCRYPTION ROW ──
    gr.Markdown("---")
    gr.Markdown("### 🔒 Secure Setup")
    gr.Markdown(
        "Enter a 4-digit PIN to encrypt your health data locally. "
        "The key is kept **in memory only** and never written to disk."
    )
    with gr.Row():
        pin_input = gr.Textbox(
            label="4-Digit PIN", type="password",
            placeholder="1234", scale=2
        )
        init_btn = gr.Button("Initialize Encryption", variant="primary", scale=1)
    init_status = gr.Markdown("")

    init_btn.click(fn=do_init_encryption, inputs=pin_input, outputs=init_status)

    gr.Markdown("---")

    # ── MAIN TWO-COLUMN LAYOUT ──
    with gr.Row():

        # LEFT COLUMN — Chat (wider)
        with gr.Column(scale=3):
            gr.ChatInterface(
                fn=do_chat,
                title="Health Agent Chat",
                examples=[
                    "Remind me to take metformin 500mg at 8am every day",
                    "Log my blood pressure: 128 over 82",
                    "Does metformin interact with ibuprofen?",
                ],
                type="messages",
            )

        # RIGHT COLUMN — Sidebar panels
        with gr.Column(scale=1):
            gr.Markdown("### 📅 Today's Reminders")
            reminders_box = gr.Textbox(
                label="Active Reminders", interactive=False, lines=6
            )

            gr.Markdown("### 📊 Recent Health Logs")
            logs_box = gr.Textbox(
                label="Last 3 Entries", interactive=False, lines=6
            )

            refresh_btn = gr.Button("🔄 Refresh Sidebar", variant="secondary")

            gr.Markdown("---")

            export_btn = gr.Button("📥 Export Summary as Text", variant="secondary")
            export_box = gr.Textbox(
                label="Export Result", interactive=False, lines=8
            )

    # Wire sidebar buttons
    refresh_btn.click(fn=do_refresh, outputs=[reminders_box, logs_box])
    export_btn.click(fn=do_export, outputs=export_box)

    # ── FOOTER ──
    gr.Markdown(
        "<center>Built with Google ADK + Gemini | MCP Server | Hugging Face Spaces"
        "<br><a href='https://github.com/Aryan24a-git/Health-agent'>GitHub Repository</a></center>"
    )

if __name__ == "__main__":
    print("Starting MediGuard Health Agent UI...")
    demo.launch(server_name="0.0.0.0", server_port=7860)
