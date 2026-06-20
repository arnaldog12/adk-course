"""Customer Support Agent - For Evaluation Testing Demonstration."""

from google.adk.agents import Agent
from tools import (
    check_ticket_status,
    create_ticket,
    list_tickets,
    search_knowledge_base,
    update_ticket,
)

root_agent = Agent(
    name="support_agent",
    model="gemini-2.5-flash",
    description=(
        "Customer support agent that can search knowledge base, create tickets, "
        "list multiple session tickets, update tickets, and check ticket status"
    ),
    instruction="""You are a helpful customer support agent. Help customers by:

1. First, try to answer their question using the knowledge base search tool
2. If you can't find relevant information, create a support ticket
3. If they mention a ticket ID, check its status or update it as requested
4. If they ask about their tickets without an ID, or want an overview, use list_tickets
5. Use update_ticket to change status, priority, or issue description of an existing ticket

Customers may have multiple open tickets in the same session. When checking or updating status,
use the exact ticket ID when provided; otherwise list their tickets first.

Always be polite, clear, and provide specific next steps. Use the tools appropriately based on the customer's needs.""",
    tools=[search_knowledge_base, create_ticket, check_ticket_status, update_ticket, list_tickets],
    output_key="support_response",
)
