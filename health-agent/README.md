# MediGuard — Personal Health & Medication Agent

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Google ADK](https://img.shields.io/badge/Google-ADK-orange) ![Hugging Face](https://img.shields.io/badge/HuggingFace-Spaces-yellow) ![License](https://img.shields.io/badge/License-CC--BY--4.0-green)

## Problem Statement

Medication non-adherence affects millions of people globally and is a leading cause of preventable health complications. Missed doses and dangerous drug interactions frequently lead to hospitalizations and worsened health outcomes. Existing health applications typically function as passive reminders or basic spreadsheets, relying entirely on the user for data entry rather than acting as intelligent, proactive agents. This creates a gap for individuals who need conversational, intuitive, and smart assistance with their daily health regimens.

## Solution

MediGuard is a multi-agent AI system designed to intelligently manage your personal health and medications. Instead of rigid menus, it uses natural language understanding to interpret requests, routing them intelligently to specialized sub-agents for scheduling, tracking, and safety verification. The system checks for drug interactions using trusted sources to ensure safety. Furthermore, all user health data is kept strictly private and local, protected by robust encryption to ensure peace of mind.

## Agent Architecture

```text
┌─────────────────────────────────────────────┐
│              User (Gradio UI)                │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│           Orchestrator Agent                 │
│     (Google ADK + Gemini 1.5 Flash)         │
│   Routes requests to the right sub-agent     │
└────────┬──────────────┬──────────┬──────────┘
         │              │          │
┌────────▼───┐  ┌───────▼──┐ ┌────▼──────────┐
│ Medication │  │  Health  │ │    Safety     │
│   Agent   │  │ Tracker  │ │   Checker     │
│           │  │  Agent   │ │    Agent      │
└────────┬──┘  └───────┬──┘ └────┬──────────┘
         │              │         │
┌────────▼──────────────▼─────────▼──────────┐
│              MCP Server Layer               │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ Storage  │ │Reminders │ │  OpenFDA   │  │
│  │  Tool   │ │  Tool    │ │    Tool    │  │
│  └──────────┘ └──────────┘ └────────────┘  │
└─────────────────────────────────────────────┘
     ↓ Encrypted local storage (Fernet)
```

## Key Features

- **Natural Language Interaction:** Talk to your health manager like a real person to set reminders or log metrics.
- **Intelligent Routing:** An orchestrator automatically detects whether your query is about scheduling, logging, or safety checks.
- **Automated Safety Checks:** Connects with the OpenFDA tool to check for known interactions between multiple medications.
- **Secure Health Logging:** Keep track of vital stats like blood pressure and heart rate with full local encryption.
- **Actionable Summaries:** Quickly generate and export a summary of your health logs and upcoming medication schedules for your doctor.
- **Privacy-First Design:** Fully local storage means your health data never leaves your device unencrypted.

## Tech Stack

| Component | Technology |
| --- | --- |
| Framework | Gradio |
| Agent Orchestration | Google ADK |
| LLM Provider | Gemini 1.5 Flash |
| Tool Abstraction | MCP (Model Context Protocol) Server |
| Encryption | cryptography (Fernet) |

## Security Design

MediGuard prioritizes user privacy and data security above all. The application utilizes a local-only storage model, ensuring that no personal health information is synchronized to the cloud. All sensitive data is protected using Fernet symmetric encryption, utilizing a passphrase-derived key stored only in memory during the active session. To maintain transparency, the system includes a comprehensive audit log of actions. Furthermore, no API keys are hardcoded in the repository; everything relies on the `.env` pattern for secure secret injection.

## Setup Instructions

1. Clone the repo
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`
4. `python main.py`
5. Open `http://localhost:7860`

## Live Demo

[Link to Hugging Face Space](https://huggingface.co/spaces/YOUR_URL_HERE) *(I will fill in the URL)*

## Course Concepts Demonstrated

| Concept | Where Demonstrated |
| --- | --- |
| Multi-agent system (ADK) | `agents/orchestrator.py` + sub-agents |
| MCP Server | `mcp_server/server.py` |
| Security features | Fernet encryption, audit log, `.env` pattern |
| Deployability | Hugging Face Spaces (live link above) |
| Agent skills | Natural language → structured health actions |

## Disclaimer

Not medical advice. For demonstration purposes only.

## License

CC-BY 4.0 — Built for Kaggle Vibecoding Agents Capstone
