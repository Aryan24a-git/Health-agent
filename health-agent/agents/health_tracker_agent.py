"""
Health Tracker Agent - ADK Component

Responsible for parsing and logging the user's health vitals (e.g., BP, glucose).
It leverages the storage tools to safely encrypt and persist data locally.
"""
from .medication_agent import Agent 

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from mcp_server.tools.storage_tool import save_health_log, get_health_logs

health_tracker_agent = Agent(
    name="health_tracker_agent",
    instructions="""You log patient vitals such as blood pressure, glucose, weight, and symptoms.
    1. Before saving any metric to the database, always confirm the value with the user.
    2. Provide simple trend summaries when asked, for example: "Your blood pressure readings this week averaged 120/80".
    """,
    tools=[save_health_log, get_health_logs],
    model="gemini-2.5-flash"
)
