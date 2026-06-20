"""Support agent tools."""

import uuid
from datetime import datetime
from typing import Any

from google.adk.tools.tool_context import ToolContext

TICKETS_STATE_KEY = "user:tickets"

VALID_PRIORITIES = ["low", "normal", "high", "urgent"]
VALID_STATUSES = ["open", "in_progress", "resolved", "closed"]

ESTIMATED_RESPONSE = {
    "low": "5 business days",
    "normal": "2 business days",
    "high": "24 hours",
    "urgent": "4 hours",
}

KNOWLEDGE_BASE = {
    "password reset": (
        "To reset your password, go to Settings > Security > Reset Password. "
        "You'll receive an email with reset instructions within 5 minutes."
    ),
    "refund policy": (
        "We offer a 30-day money-back guarantee on all purchases. "
        "Contact support@example.com with your order number to initiate a refund."
    ),
    "shipping": (
        "Standard shipping takes 3-5 business days. Express shipping (1-2 days) "
        "is available for an additional $10. Track your order at example.com/track"
    ),
    "account": (
        "Manage your account settings at example.com/account. "
        "You can update your profile, payment methods, and notification preferences."
    ),
    "billing": (
        "View your billing history and invoices at example.com/billing. "
        "Contact billing@example.com for payment-related questions."
    ),
    "technical support": (
        "For technical issues, please provide your system details and error messages. "
        "Our support team will respond within 24 hours."
    ),
}


# ============================================================================
# Internal helpers
# ============================================================================


def _get_tickets(tool_context: ToolContext) -> dict[str, Any]:
    """Return a copy of the session ticket store."""
    tickets = tool_context.state.get(TICKETS_STATE_KEY)
    return dict(tickets) if tickets else {}


def _save_tickets(tool_context: ToolContext, tickets: dict[str, Any]) -> None:
    """Persist ticket updates through ADK state delta."""
    tool_context.state[TICKETS_STATE_KEY] = tickets


def _find_ticket(tickets: dict[str, Any], ticket_id: str) -> tuple[str, dict[str, Any]] | None:
    """Find a ticket by ID, matching case-insensitively."""
    normalized_id = ticket_id.strip().upper()
    for stored_id, ticket in tickets.items():
        if stored_id.upper() == normalized_id:
            return stored_id, ticket
    return None


def _not_found_response(ticket_id: str, tickets: dict[str, Any]) -> dict[str, Any]:
    """Build a consistent 'ticket not found' error response."""
    available_ids = sorted(tickets.keys())
    if available_ids:
        ids_text = ", ".join(available_ids)
        report = f"Could not find ticket {ticket_id}. Available tickets in this session: {ids_text}."
    else:
        report = f"Could not find ticket {ticket_id}. No tickets exist in this session yet."
    return {
        "status": "error",
        "error": f"Ticket {ticket_id} not found",
        "report": report,
        "available_ticket_ids": available_ids,
    }


# ============================================================================
# Tools
# ============================================================================


def search_knowledge_base(query: str, tool_context: ToolContext) -> dict[str, Any]:
    """Search the knowledge base for information about common customer issues.

    Args:
        query: The search query to look for in the knowledge base. It can be one of the following:
            - password reset
            - refund policy
            - shipping
            - account
            - billing
            - technical support
        tool_context: ADK tool context

    Returns:
        Dict with status, report, and search results
    """
    query_lower = query.lower()
    results = [
        {"topic": key, "content": content}
        for key, content in KNOWLEDGE_BASE.items()
        if key in query_lower or any(word in query_lower for word in key.split())
    ]

    if results:
        return {
            "status": "success",
            "report": f'Found {len(results)} relevant article(s) for "{query}"',
            "results": results,
        }
    return {
        "status": "success",
        "report": f'No articles found for "{query}". Please try rephrasing your question or contact support.',
        "results": [],
    }


def create_ticket(issue: str, tool_context: ToolContext, priority: str = "normal") -> dict[str, Any]:
    """Create a new support ticket for customer issues.

    Args:
        issue: Description of the customer's issue
        priority: Priority level (low, normal, high, urgent)
        tool_context: ADK tool context

    Returns:
        Dict with status, report, and ticket details
    """
    if priority not in VALID_PRIORITIES:
        return {
            "status": "error",
            "error": f'Invalid priority "{priority}". Must be one of: {", ".join(VALID_PRIORITIES)}',
            "report": f'Failed to create ticket: invalid priority "{priority}"',
        }

    ticket_id = f"TICK-{uuid.uuid4().hex[:8].upper()}"
    ticket = {
        "ticket_id": ticket_id,
        "issue": issue,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "estimated_response": ESTIMATED_RESPONSE.get(priority, "2 business days"),
    }

    tickets = _get_tickets(tool_context)
    tickets[ticket_id] = ticket
    _save_tickets(tool_context, tickets)

    ticket_count = len(tickets)
    report = (
        f"Ticket {ticket_id} created successfully with {priority} priority. "
        f"Expected response time: {ticket['estimated_response']}"
    )
    if ticket_count > 1:
        report += f" You now have {ticket_count} ticket(s) in this session."

    return {
        "status": "success",
        "report": report,
        "ticket": ticket,
        "ticket_count": ticket_count,
    }


def update_ticket(
    ticket_id: str,
    tool_context: ToolContext,
    status: str | None = None,
    priority: str | None = None,
    issue: str | None = None,
) -> dict[str, Any]:
    """Update an existing support ticket's status, priority, or issue description.

    Args:
        ticket_id: The ID of the ticket to update
        tool_context: ADK tool context
        status: New status for the ticket (open, in_progress, resolved, closed)
        priority: New priority level (low, normal, high, urgent)
        issue: Updated description of the issue

    Returns:
        Dict with status, report, and updated ticket details
    """
    if status is None and priority is None and issue is None:
        return {
            "status": "error",
            "error": "No fields to update",
            "report": "Please provide at least one field to update: status, priority, or issue.",
        }

    if status is not None and status not in VALID_STATUSES:
        return {
            "status": "error",
            "error": f'Invalid status "{status}". Must be one of: {", ".join(VALID_STATUSES)}',
            "report": f'Failed to update ticket: invalid status "{status}"',
        }

    if priority is not None and priority not in VALID_PRIORITIES:
        return {
            "status": "error",
            "error": f'Invalid priority "{priority}". Must be one of: {", ".join(VALID_PRIORITIES)}',
            "report": f'Failed to update ticket: invalid priority "{priority}"',
        }

    tickets = _get_tickets(tool_context)
    match = _find_ticket(tickets, ticket_id)

    if match is None:
        return _not_found_response(ticket_id, tickets)

    resolved_id, ticket = match
    changes = []

    if status is not None and ticket["status"] != status:
        changes.append(f"status: {ticket['status']} → {status}")
        ticket["status"] = status

    if priority is not None and ticket["priority"] != priority:
        changes.append(f"priority: {ticket['priority']} → {priority}")
        ticket["priority"] = priority
        ticket["estimated_response"] = ESTIMATED_RESPONSE.get(priority, "2 business days")

    if issue is not None and ticket["issue"] != issue:
        changes.append("issue description updated")
        ticket["issue"] = issue

    if not changes:
        return {
            "status": "success",
            "report": f"Ticket {resolved_id} already has the requested values. No changes made.",
            "ticket": ticket,
        }

    ticket["updated_at"] = datetime.now().isoformat()
    tickets[resolved_id] = ticket
    _save_tickets(tool_context, tickets)

    changes_text = ", ".join(changes)
    return {
        "status": "success",
        "report": f"Ticket {resolved_id} updated successfully. Changes: {changes_text}.",
        "ticket": ticket,
    }


def check_ticket_status(ticket_id: str, tool_context: ToolContext) -> dict[str, Any]:
    """Check the status of an existing support ticket.

    Args:
        ticket_id: The ticket ID to check
        tool_context: ADK tool context

    Returns:
        Dict with status, report, and ticket information
    """
    tickets = _get_tickets(tool_context)
    match = _find_ticket(tickets, ticket_id)

    if match is None:
        return _not_found_response(ticket_id, tickets)

    resolved_id, ticket = match
    return {
        "status": "success",
        "report": f"Ticket {resolved_id} is currently {ticket['status']} (Priority: {ticket['priority']})",
        "ticket": ticket,
    }


def list_tickets(
    tool_context: ToolContext,
    status: str | None = None,
    priority: str | None = None,
) -> dict[str, Any]:
    """List all support tickets in the current session.

    Args:
        tool_context: ADK tool context
        status: Optional filter by ticket status (open, in_progress, resolved, closed)
        priority: Optional filter by priority (low, normal, high, urgent)

    Returns:
        Dict with status, report, and matching tickets
    """
    tickets = _get_tickets(tool_context)

    if not tickets:
        return {
            "status": "success",
            "report": "No support tickets found in this session.",
            "tickets": [],
            "count": 0,
        }

    filtered = list(tickets.values())

    if status is not None:
        filtered = [t for t in filtered if t["status"].lower() == status.lower()]

    if priority is not None:
        filtered = [t for t in filtered if t["priority"].lower() == priority.lower()]

    filtered.sort(key=lambda t: t["created_at"], reverse=True)

    if not filtered:
        filters = []
        if status is not None:
            filters.append(f"status={status}")
        if priority is not None:
            filters.append(f"priority={priority}")
        return {
            "status": "success",
            "report": f"No tickets found matching filters: {', '.join(filters)}.",
            "tickets": [],
            "count": 0,
        }

    return {
        "status": "success",
        "report": f"Found {len(filtered)} ticket(s) in this session.",
        "tickets": filtered,
        "count": len(filtered),
    }
