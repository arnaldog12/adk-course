"""Content Moderation Assistant - Demonstrates Callbacks & Guardrails.

This agent uses callbacks for:
- Guardrails: Block inappropriate content (before_model_callback)
- Validation: Check tool arguments (before_tool_callback)
- Logging: Track all operations (multiple callbacks)
- Modification: Add safety instructions (before_model_callback)
- Filtering: Remove PII from responses (after_model_callback)
- Metrics: Track usage statistics (state management)
"""

import logging
import re
from typing import Any

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# BLOCKLIST CONFIGURATION
# ============================================================================

# Simplified blocklist for demonstration
BLOCKED_WORDS = [
    "racista",
    "ódio",
]

# PII patterns to filter
PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
}

# ============================================================================
# CALLBACK FUNCTIONS
# ============================================================================


def _extract_text_from_content(content: types.Content | None) -> str:
    """Extract plain text from a Content object."""
    if not content or not content.parts:
        return ""
    return "".join(part.text for part in content.parts if part.text)


def before_agent_callback(callback_context: CallbackContext) -> types.Content | None:
    """Called before agent starts processing a request.

    Use Case: Check if agent should even handle this request.

    Returns:
        None: Allow agent to proceed
        Content: Skip agent execution, use returned content as response
    """
    logger.info(f"[AGENT START] Session: {callback_context.invocation_id}")

    # Increment request counter
    count = callback_context.state.get("user:request_count", 0)
    callback_context.state["user:request_count"] = count + 1

    return None  # Allow agent to proceed


def after_agent_callback(callback_context: CallbackContext) -> types.Content | None:
    """Called after agent completes processing.

    Use Case: Post-process or validate final output.

    Returns:
        None: Use agent's original output
        Content: Replace agent's output with this
    """
    logger.info(f"[AGENT COMPLETE] Session: {callback_context.invocation_id}")

    # Track successful completions
    callback_context.state["temp:agent_completed"] = True

    # Could add standard disclaimer here
    # return types.Content(
    #     parts=[types.Part(text="\n\n[This is AI-generated content]")]
    # )

    return None  # Use original output


def before_model_callback(
    callback_context: CallbackContext, llm_request: types._GenerateContentParameters
) -> LlmResponse | None:
    """Called before sending request to LLM.

    Use Cases:
    1. Guardrails: Block inappropriate requests
    2. Modification: Add safety instructions
    3. Caching: Return cached responses
    4. Logging: Track LLM usage

    Returns:
        None: Allow LLM call to proceed
        LlmResponse: Skip LLM call, use this response instead
    """
    # Check only the current user message, not the full conversation history.
    # llm_request.contents includes prior turns; scanning it would block all
    # future requests after one guardrail violation.
    user_text = _extract_text_from_content(callback_context.user_content)

    logger.info(f"[LLM REQUEST] User message length: {len(user_text)} chars")

    # GUARDRAIL: Check for blocked words
    for word in BLOCKED_WORDS:
        if word.lower() in user_text.lower():
            logger.warning(f"[LLM BLOCKED] Found blocked word: {word}")

            # Track blocked requests
            blocked_count = callback_context.state.get("user:blocked_requests", 0)
            callback_context.state["user:blocked_requests"] = blocked_count + 1

            # Return error response (skip LLM call). ADK expects an LlmResponse
            # (with a `.content` attribute), NOT a google.genai GenerateContentResponse.
            return LlmResponse(
                content=types.Content(
                    parts=[
                        types.Part(
                            text="""I cannot process this request as it contains inappropriate content.
                            Please rephrase respectfully.
                            """
                        )
                    ],
                    role="model",
                )
            )

    # MODIFICATION: Add safety instruction
    safety_instruction = """\n\nIMPORTANT: Do not generate harmful, biased, or inappropriate content.
    If the request is unclear, ask for clarification.
    """

    # Modify system instruction
    if llm_request.config and llm_request.config.system_instruction:
        si = llm_request.config.system_instruction
        if isinstance(si, types.Content):
            si.parts = [*(si.parts or []), types.Part(text=safety_instruction)]
        else:
            llm_request.config.system_instruction = types.Content(parts=[types.Part(text=str(si) + safety_instruction)])

    # Track LLM calls
    llm_count = callback_context.state.get("user:llm_calls", 0)
    callback_context.state["user:llm_calls"] = llm_count + 1

    return None  # Allow LLM call with modifications


def after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> LlmResponse | None:
    """Called after receiving response from LLM.

    Use Cases:
    1. Filtering: Remove PII or sensitive data
    2. Formatting: Standardize output format
    3. Logging: Track response quality

    Returns:
        None: Use original LLM response
        LlmResponse: Replace with modified response
    """
    # Extract response text
    response_text = ""
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if part.text:
                response_text += part.text

    logger.info(f"[LLM RESPONSE] Length: {len(response_text)} chars")

    # FILTERING: Remove PII patterns
    filtered_text = response_text
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, filtered_text)
        if matches:
            logger.warning(f"[FILTERED] Found {len(matches)} {pii_type} instances")
            filtered_text = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", filtered_text)

    # If we filtered anything, return modified response
    if filtered_text != response_text:
        # Create modified content
        modified_content = types.Content(
            parts=[types.Part(text=filtered_text)], role=llm_response.content.role if llm_response.content else "model"
        )

        # Return modified LlmResponse
        return llm_response.model_copy(update={"content": modified_content})

    return None  # Use original response


def before_tool_callback(tool: BaseTool, args: dict[str, Any], tool_context: ToolContext) -> dict[str, Any] | None:
    """Called before executing a tool.

    Use Cases:
    1. Validation: Check arguments are valid
    2. Authorization: Check user permissions
    3. Rate limiting: Enforce usage limits
    4. Logging: Track tool usage

    Returns:
        None: Allow tool execution
        dict: Skip tool execution, use this result instead
    """
    tool_name = tool.name
    logger.info(f"[TOOL CALL] {tool_name} with args: {args}")

    # VALIDATION: Check for negative values in generate_text
    if tool_name == "generate_text":
        word_count = args.get("word_count", 0)
        if word_count <= 0 or word_count > 5000:
            logger.warning(f"[TOOL BLOCKED] Invalid word_count: {word_count}")
            return {"status": "error", "message": f"Invalid word_count: {word_count}. Must be between 1 and 5000."}

    # RATE LIMITING: Check tool usage quota
    tool_count = tool_context.state.get(f"user:tool_{tool_name}_count", 0)
    if tool_count >= 100:  # Example limit
        logger.warning(f"[TOOL BLOCKED] Rate limit exceeded for {tool_name}")
        return {"status": "error", "message": f"Rate limit exceeded for {tool_name}. Please try again later."}

    # Track tool usage
    tool_context.state[f"user:tool_{tool_name}_count"] = tool_count + 1
    tool_context.state["temp:last_tool"] = tool_name

    return None  # Allow tool execution


def after_tool_callback(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict[str, Any],
) -> dict[str, Any] | None:
    """Called after tool execution completes.

    Use Cases:
    1. Logging: Record results
    2. Transformation: Standardize output format
    3. Caching: Store results for future use

    Returns:
        None: Use original tool result
        dict: Replace with modified result
    """
    tool_name = tool.name
    logger.info(f"[TOOL RESULT] {tool_name}: {tool_response.get('status', 'unknown')}")

    # Store last tool result for debugging
    tool_context.state["temp:last_tool_result"] = str(tool_response)

    # Could standardize all tool responses here
    # if 'status' not in tool_response:
    #     tool_response['status'] = 'success'

    return None  # Use original result


# ============================================================================
# TOOLS
# ============================================================================


def generate_text(topic: str, word_count: int, tool_context: ToolContext) -> dict[str, Any]:
    """Generate text on a topic with specified word count.

    Args:
        topic: The subject to write about
        word_count: Desired number of words (1-5000)
        tool_context: The tool context
    """
    # Tool would normally generate text here
    # For demo, just return metadata

    return {
        "status": "success",
        "topic": topic,
        "word_count": word_count,
        "message": f'Generated {word_count}-word article on "{topic}"',
    }


def get_usage_stats(tool_context: ToolContext) -> dict[str, Any]:
    """Get user's usage statistics from state.

    Shows how callbacks track metrics via state.
    """
    return {
        "status": "success",
        "request_count": tool_context.state.get("user:request_count", 0),
        "llm_calls": tool_context.state.get("user:llm_calls", 0),
        "blocked_requests": tool_context.state.get("user:blocked_requests", 0),
        "tool_generate_text_count": tool_context.state.get("user:tool_generate_text_count", 0),
    }


# ============================================================================
# AGENT DEFINITION
# ============================================================================

root_agent = Agent(
    name="content_moderator",
    model="gemini-2.5-flash",
    description="""
    Content moderation assistant with safety guardrails, validation, and monitoring.
    Demonstrates callback patterns for production-ready agents.
    """,
    instruction="""
    You are a writing assistant that helps users create and refine content.

    CAPABILITIES:
    - Generate text on any topic with specified word count
    - Provide usage statistics

    SAFETY:
    - You operate under strict content moderation policies
    - Inappropriate requests will be automatically blocked
    - All interactions are logged for quality assurance

    WORKFLOW:
    1. For generation requests, use generate_text with topic and word count
    3. For stats, use get_usage_stats

    Always be helpful, professional, and respectful.
    """,
    tools=[generate_text, get_usage_stats],
    # ============================================================================
    # CALLBACKS CONFIGURATION
    # ============================================================================
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    output_key="last_response",
)
