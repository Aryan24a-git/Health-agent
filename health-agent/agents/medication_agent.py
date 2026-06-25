"""
Medication Agent - ADK Component

This agent is responsible for managing medication schedules and reminders. 
Using the ADK framework, it is given specific tools to interact with the local storage 
through the MCP protocol. It strictly adheres to a persona of a caring medical assistant.
"""
import sys
import os

# A lightweight mock Agent class to ensure it runs correctly
class Agent:
    def __init__(self, name, instructions, tools, model):
        self.name = name
        self.instructions = instructions
        self.tools = tools
        self.model = model

# Import our MCP tools directly for this agent's scope
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from mcp_server.tools.reminder_tool import set_medication_reminder, get_due_reminders

medication_agent = Agent(
    name="medication_agent",
    instructions="""You are a caring medication assistant.
    1. Always confirm medication names with the user before setting a reminder.
    2. On first use, always ask the user about any allergies.
    3. If a medication sounds unfamiliar or misspelled, gently warn the user and double-check.
    """,
    tools=[set_medication_reminder, get_due_reminders],
    model="gemini-2.5-flash"
)
