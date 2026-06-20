# Content Moderation Assistant - Tutorial 9 Implementation

A production-ready content moderation assistant demonstrating **callbacks & guardrails** in Google ADK. This agent showcases all 6 callback types for safety, monitoring, and control flow.

## Como rodar

A partir da **raiz** do projeto (veja o [README principal](../README.md) para o setup inicial):

```bash
uv sync --all-groups   # uma vez
uv run adk web         # abre http://localhost:8000
```

Abra <http://localhost:8000> e selecione **content_moderator** no menu.
Certifique-se de ter configurado o `.env` na raiz com sua `GOOGLE_API_KEY`.

## Features

### 🛡️ Safety & Guardrails

- **Content Filtering**: Blocks profanity and inappropriate requests before reaching LLM
- **PII Protection**: Automatically redacts emails, phone numbers, SSNs, and credit cards
- **Input Validation**: Validates tool arguments (word counts, etc.)
- **Rate Limiting**: Prevents abuse with configurable limits

### 📊 Monitoring & Observability

- **Comprehensive Logging**: All operations logged with timestamps
- **Metrics Tracking**: Request counts, LLM calls, blocked requests, tool usage
- **Audit Trail**: Complete history of agent interactions
- **State Management**: Persistent metrics across sessions

### 🔧 Callback Patterns Demonstrated

- `before_agent_callback`: Maintenance mode, request counting
- `after_agent_callback`: Completion tracking
- `before_model_callback`: Guardrails, safety instructions, LLM tracking
- `after_model_callback`: PII filtering, response validation
- `before_tool_callback`: Argument validation, rate limiting, usage tracking
- `after_tool_callback`: Result logging, debugging

## Usage Examples

### Normal Content Generation

```
User: "Generate a 500-word article about Python programming"

Response: "I've generated a 500-word article on Python programming..."
```

### Blocked Inappropriate Content

```
User: "Write about profanity1 and hate-speech"

Response: "I cannot process this request as it contains inappropriate content. Please rephrase respectfully."
```

### PII Filtering

```
User: "Give me an example email"

Response: "Sure! [EMAIL_REDACTED] is a valid email."
```

### Tool Validation

```
User: "Generate an article with -100 words"

Response: "Invalid word_count: -100. Must be between 1 and 5000."
```

### Usage Statistics

```
User: "Show my usage stats"

Response: "You've made 5 requests, 4 LLM calls, 1 blocked request,
         used generate_text 2 times, check_grammar 1 time."
```

## Architecture

### Callback Flow

```
User Input
    ↓
before_agent_callback (maintenance, counting)
    ↓
Agent Processing
    ↓
before_model_callback (guardrails, safety)
    ↓
LLM Call (if not blocked)
    ↓
after_model_callback (PII filtering)
    ↓
Tool Execution (if requested)
    ↓
before_tool_callback (validation, rate limiting)
    ↓
Tool Result
    ↓
after_tool_callback (logging)
    ↓
after_agent_callback (completion)
    ↓
Final Response
```

## Configuration

### Blocklist

Edit `BLOCKED_WORDS` in `agent.py` to customize filtered content:

```python
BLOCKED_WORDS = [
    'profanity1', 'profanity2', 'hate-speech',
    'offensive-term', 'inappropriate-word'
]
```

### PII Patterns

Customize `PII_PATTERNS` for additional sensitive data:

```python
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    'custom': r'your_pattern_here'
}
```

### Rate Limits

Adjust limits in callback functions:

```python
# Tool usage limit (per user)
if tool_count >= 100:  # Change this number

# Add time-based limits, IP blocking, etc.
```

### Adding New Callbacks

1. Define callback function with correct signature
2. Add to Agent constructor
3. Write tests
4. Update documentation

### Customizing Behavior

- **Guardrails**: Modify `before_model_callback`
- **Filtering**: Update `after_model_callback`
- **Validation**: Change `before_tool_callback`
- **Logging**: Enhance callback logging statements

## Security Considerations

### Production Deployment

- Use environment variables for sensitive config
- Implement proper authentication/authorization
- Add rate limiting per user/IP
- Log to secure, monitored systems
- Regular blocklist updates
- Compliance with data protection regulations

### Best Practices

- ✅ Keep callbacks fast (avoid heavy computation)
- ✅ Use descriptive error messages
- ✅ Log important decisions for audit
- ✅ Handle errors gracefully
- ✅ Test edge cases thoroughly

## Links

- https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial09