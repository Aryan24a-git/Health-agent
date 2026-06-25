# 🩺 Personal Health & Medication Manager
A privacy-first AI agent that tracks health vitals, schedules medication reminders, and checks drug interactions entirely locally.

![Built for Kaggle Vibecoding Agents Capstone](https://img.shields.io/badge/Kaggle-Vibecoding_Agents_Capstone-blue?style=for-the-badge)

## The Problem
Managing multiple medications, tracking vitals, and navigating potential drug interactions is overwhelming for patients. External apps often demand cloud access to highly sensitive health data. We need a conversational assistant that respects absolute privacy.

## Architecture Diagram
```text
[ User ] <--> [ Gradio UI (Input Sanitization, Rate Limits) ]
                    |
                    v
          [ Orchestrator Agent ]
         /          |           \
        /           |            \
[Medication] [HealthTracker] [SafetyChecker]
   |                |               |
   v                v               v
[ MCP Server: Local Tools, OpenFDA API, Audit Logging ]
```

## Setup Instructions
1. Clone the repository: `git clone <your-repo-url> && cd health-agent`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure API: `cp .env.example .env` and add your GEMINI_API_KEY
4. Run the app: `python main.py`

## Security Design
- **Local Storage**: Data never leaves the `data/` folder.
- **Fernet Encryption**: Health logs are encrypted in memory using a user's PIN.
- **Input Sanitization**: Protects against injection.
- **Audit Logging**: Tool executions are logged securely.
- For more details, see [SECURITY.md](SECURITY.md).

## Screenshot
![App Screenshot Placeholder](screenshot.png)
