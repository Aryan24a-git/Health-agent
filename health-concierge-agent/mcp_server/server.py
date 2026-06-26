"""
MCP (Model Context Protocol) Server Integration

This file initializes the MCP server for the Personal Health Agent.
Why we use MCP:
The Model Context Protocol allows us to cleanly decouple tools from the agents. 
Instead of hardcoding APIs or storage logic directly into the agents, we expose them 
as standard MCP endpoints. This is highly secure and scalable, as the agents only 
interact with the tools through the protocol layer.
"""

from mcp.server.fastmcp import FastMCP
from tools.storage_tool import save_health_log, get_health_logs
from tools.drug_api_tool import check_drug_interaction
from tools.reminder_tool import set_medication_reminder, get_due_reminders

# Initialize the FastMCP server
mcp = FastMCP("PersonalHealthMCP")

# Register our tools
mcp.tool()(save_health_log)
mcp.tool()(get_health_logs)
mcp.tool()(check_drug_interaction)
mcp.tool()(set_medication_reminder)
mcp.tool()(get_due_reminders)

if __name__ == "__main__":
    # In a full deployment, this runs as a separate process or via stdio.
    mcp.run(transport='stdio')
