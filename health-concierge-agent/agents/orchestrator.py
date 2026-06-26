"""
Orchestrator Agent - ADK Multi-Agent Router

This is the root ADK agent. In the multi-agent routing pattern, the orchestrator acts as the front-door 
to the user. Instead of answering domain-specific queries directly, it analyzes the user's intent and 
routes the query to the appropriate sub-agent (Medication, Health Tracker, or Safety Checker). 

This pattern is highly scalable and ensures that complex, multi-step requests (e.g., "Add metformin AND check interactions") 
are correctly broken down and dispatched.
"""
from .medication_agent import Agent, medication_agent
from .health_tracker_agent import health_tracker_agent
from .safety_checker_agent import safety_checker_agent

orchestrator = Agent(
    name="orchestrator",
    instructions="""You are the main Personal Health Concierge orchestrator.
    1. Introduce yourself warmly on the very first message.
    2. You possess three sub-agents as tools: medication_agent, health_tracker_agent, and safety_checker_agent.
    3. Decide which sub-agent to route requests to based on user intent.
    4. If the user makes a multi-step request (e.g., "add my metformin reminder AND check if it interacts with aspirin"), 
       coordinate the execution by calling the relevant sub-agents sequentially and summarizing the results.
    """,
    tools=[medication_agent, health_tracker_agent, safety_checker_agent],
    model="gemini-2.5-flash"
)
