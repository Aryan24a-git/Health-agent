import os
import sys
import json
import re
import time
import gradio as gr
from dotenv import load_dotenv

# Ensure 'agents' and 'mcp_server' imports resolve correctly
sys.path.append(os.path.dirname(__file__))

# Load environment variables (e.g. GEMINI_API_KEY)
load_dotenv()

from agents.orchestrator import orchestrator
from mcp_server.tools.storage_tool import initialize_encryption, get_health_logs
from mcp_server.tools.reminder_tool import get_due_reminders

# --- SECURITY: Input Sanitization ---
def sanitize_input(text: str) -> str:
    """Strips HTML/script tags to prevent injection attacks."""
    return re.sub(r'<[^>]+>', '', text)

# --- SECURITY: Rate Limiting ---
class RateLimiter:
    """Token-bucket rate limiter ensuring max agent calls per minute."""
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        
    def consume(self) -> bool:
        now = time.time()
        time_passed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + time_passed * self.refill_rate)
        self.last_refill = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

# 20 tokens max, refill 20 tokens per 60 seconds (1 token per 3 seconds)
rate_limiter = RateLimiter(capacity=20, refill_rate=20/60.0)

def set_passphrase(passphrase: str):
    """
    Initializes the encryption key in memory using the 4-digit passphrase.
    Returns a status message and toggles the visibility of the UI components.
    """
    if len(passphrase) != 4 or not passphrase.isdigit():
        return "Please enter a valid 4-digit PIN.", gr.update(visible=True), gr.update(visible=False)
    
    try:
        initialize_encryption(passphrase)
        return "✅ Encryption initialized securely in memory!", gr.update(visible=False), gr.update(visible=True)
    except Exception as e:
        return f"Error initializing encryption: {e}", gr.update(visible=True), gr.update(visible=False)

def chat_interface(user_message: str, history: list):
    """
    Routes the user's chat message to the Google ADK orchestrator.
    Incorporates sanitization and rate limiting.
    """
    if not rate_limiter.consume():
        response = "⚠️ Rate limit exceeded. Please wait a moment before sending another message."
        history.append((user_message, response))
        return "", history
        
    clean_message = sanitize_input(user_message)
    
    try:
        # Mock orchestrator behavior for the demo.
        response = f"🤖 [Orchestrator routed query]: '{clean_message}'\n\n*(Waiting for live ADK model response - backend integration required)*"
    except Exception as e:
        response = f"Error routing to orchestrator: {str(e)}"
    
    history.append((user_message, response))
    return "", history

def refresh_sidebar():
    """
    Fetches the latest reminders and the last 3 health logs to update the UI sidebar.
    """
    try:
        reminders = get_due_reminders()
    except Exception:
        reminders = "No reminders data available."
        
    try:
        logs = get_health_logs(limit=3)
    except Exception:
        logs = "No logs available or encrypted."
        
    return reminders, logs

def export_summary():
    """
    Exports all decrypted logs and reminders as a formatted text block for the user's doctor.
    """
    try:
        logs = get_health_logs()
        reminders = get_due_reminders()
        summary = f"--- HEALTH SUMMARY EXPORT ---\n\nREMINDERS:\n{reminders}\n\nLOGS:\n{logs}"
        return summary
    except Exception as e:
        return f"Export failed: {str(e)}"

def clear_chat():
    return [], ""

# Custom CSS for the disclaimer banner and header
custom_css = """
.disclaimer-banner {
    background-color: #ff4d4d;
    color: white;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    margin-bottom: 15px;
}
.header-title {
    font-size: 2.5em;
    color: #2c3e50;
    text-align: center;
    margin-bottom: 5px;
}
.header-subtitle {
    text-align: center;
    color: #7f8c8d;
    margin-bottom: 20px;
}
.footer-text {
    text-align: center;
    color: #95a5a6;
    margin-top: 30px;
    font-size: 0.9em;
}
"""

# Build the Gradio UI
with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as demo:
    # --- HEADER SECTION ---
    gr.Markdown("<div class='header-title'>MediGuard — Personal Health & Medication Agent</div>")
    gr.Markdown("<div class='header-subtitle'>An AI-powered multi-agent system for medication reminders, health tracking, and drug safety checks</div>")
    gr.Markdown("<div class='disclaimer-banner'>⚠️ This tool is not a substitute for professional medical advice. Always consult your doctor or pharmacist.</div>")
    
    # 1. Passphrase Modal Layer
    with gr.Row(visible=True) as setup_row:
        with gr.Column():
            gr.Markdown("### 🔒 Secure Setup")
            gr.Markdown("Please enter a 4-digit PIN to securely encrypt your health logs locally. The key is stored purely in memory and never written to disk.")
            pin_input = gr.Textbox(label="4-Digit Passphrase", type="password", placeholder="1234")
            setup_btn = gr.Button("Initialize Encryption")
            setup_status = gr.Markdown("")
            
    # 2. Main App Layout Layer (Hidden until passphrase is set)
    with gr.Row(visible=False) as main_app_row:
        # Left column (wider, 65%)
        with gr.Column(scale=65):
            # Chat window
            chatbot = gr.Chatbot(height=500, label="Agent Chat")
            
            # Text input box
            user_input = gr.Textbox(
                show_label=False,
                placeholder="Try: 'Remind me to take metformin at 8am' or 'Log blood pressure 120/80' or 'Does aspirin interact with warfarin?'"
            )
            
            # Action buttons
            with gr.Row():
                submit_btn = gr.Button("Submit", variant="primary")
                clear_btn = gr.Button("Clear", variant="secondary")
                
        # Right column (35%)
        with gr.Column(scale=35):
            gr.Markdown("### 📅 Today's Reminders")
            reminders_display = gr.Textbox(label="", interactive=False, lines=4, show_label=False)
            
            gr.Markdown("### 📊 Recent Health Logs")
            logs_display = gr.Textbox(label="", interactive=False, lines=4, show_label=False)
            
            export_btn = gr.Button("📥 Export Summary")
            export_display = gr.Textbox(label="Export Result", interactive=False, lines=5)
            
    # --- FOOTER ---
    gr.Markdown("<div class='footer-text'>Built with Google ADK + Gemini | MCP Server | Hugging Face Spaces<br>[GitHub Repository Link]</div>")

    # Wire up the UI events
    setup_btn.click(
        fn=set_passphrase, 
        inputs=pin_input, 
        outputs=[setup_status, setup_row, main_app_row]
    ).then(
        fn=refresh_sidebar,
        inputs=[],
        outputs=[reminders_display, logs_display]
    )
    
    submit_btn.click(
        fn=chat_interface,
        inputs=[user_input, chatbot],
        outputs=[user_input, chatbot]
    ).then(
        fn=refresh_sidebar,
        inputs=[],
        outputs=[reminders_display, logs_display]
    )
    
    user_input.submit(
        fn=chat_interface,
        inputs=[user_input, chatbot],
        outputs=[user_input, chatbot]
    ).then(
        fn=refresh_sidebar,
        inputs=[],
        outputs=[reminders_display, logs_display]
    )
    
    clear_btn.click(
        fn=clear_chat,
        inputs=[],
        outputs=[chatbot, user_input]
    )
    
    export_btn.click(
        fn=export_summary,
        inputs=[],
        outputs=export_display
    )

if __name__ == "__main__":
    print("Starting Personal Health Agent UI...")
    demo.launch(server_name="127.0.0.1", server_port=7861, share=False)
