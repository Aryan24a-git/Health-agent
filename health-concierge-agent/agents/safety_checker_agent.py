"""
Safety Checker Agent - ADK Component

A highly constrained agent dedicated entirely to querying drug interactions using OpenFDA.
By isolating this logic into a dedicated ADK agent, we reduce hallucinations and ensure safety 
disclaimers are strictly enforced.

SAFETY DISCLAIMER: This agent provides informational API results and is NOT a substitute for professional medical advice.
"""
from .medication_agent import Agent

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from mcp_server.tools.drug_api_tool import check_drug_interaction

safety_checker_agent = Agent(
    name="safety_checker_agent",
    instructions="""You check drug interactions using the OpenFDA API.
    1. Always remind the user that you are NOT a doctor and they should consult a pharmacist or physician.
    2. If the API returns any WARNING or CONTRAINDICATION, you must flag it prominently in bold and red text (if possible) to ensure the user notices it.
    """,
    tools=[check_drug_interaction],
    model="gemini-2.5-flash"
)
