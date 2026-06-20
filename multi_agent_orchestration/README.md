# Tutorial 06: Multi-Agent Systems - Content Publishing System

This implementation demonstrates sophisticated multi-agent orchestration by combining Sequential and Parallel agents in nested workflows. The content publishing system runs parallel research pipelines (news, social, expert) then creates content through sequential refinement (write, edit, format).

## Overview

The content publishing system showcases:

- **Nested Agent Orchestration**: Sequential agents inside Parallel agents
- **Multi-Phase Workflows**: Parallel research → Sequential content creation
- **State Management**: Complex data flow between nested agent layers
- **Production-Ready Architecture**: Real-world content generation pipeline

## Architecture

```
User Query: "Write article about AI in healthcare"
    ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: Parallel Research (3 Sequential Pipelines)    │
├─────────────────────────────────────────────────────────┤
│  News Pipeline:    fetch → summarize → news_summary     │
│  Social Pipeline:  monitor → analyze → social_insights  │ ← ALL RUN
│  Expert Pipeline:  find → extract → expert_quotes       │   AT ONCE!
└─────────────────────────────────────────────────────────┘
    ↓ (waits for ALL 3 to complete)
┌─────────────────────────────────────────────────────────┐
│  PHASE 2: Sequential Content Creation                   │
├─────────────────────────────────────────────────────────┤
│  Writer:    combines all research → draft_article       │
│  Editor:    reviews draft → edited_article              │ ← ONE AT
│  Formatter: adds markdown → published_article           │   A TIME
└─────────────────────────────────────────────────────────┘
    ↓
Final Output: Publication-ready article!
```

## Quick Start

1. **Install dependencies:**

   ```bash
   make setup
   ```

2. **Configure API key:**

   ```bash
   cp content_publisher/.env.example content_publisher/.env
   # Edit content_publisher/.env and add your Google AI API key
   ```

3. **Start development server:**

   ```bash
   make dev
   ```

4. **Open [http://localhost:8000](http://localhost:8000)** and select "content_publisher"

## Example Prompts

Try these prompts to see multi-agent orchestration in action:

- `"Write an article about artificial intelligence in healthcare"`
- `"Create an article about renewable energy adoption"`
- `"Write about the future of remote work"`
- `"Create an article explaining quantum computing breakthroughs"`

## How It Works

### Phase 1: Parallel Research

The system runs three research pipelines simultaneously:

- **News Pipeline**: Fetches current articles → Summarizes key points
- **Social Pipeline**: Monitors trends → Analyzes sentiment
- **Expert Pipeline**: Finds opinions → Extracts quotes

### Phase 2: Sequential Content Creation

After all research completes, content is created through sequential refinement:

- **Writer**: Synthesizes all research into a draft article
- **Editor**: Improves clarity, flow, and impact
- **Formatter**: Adds publication formatting and structure

### Performance Benefits

- **Without orchestration**: ~90 seconds (9 agents sequentially)
- **With multi-agent orchestration**: ~35 seconds (6 research agents parallel + 3 creation sequential)
- **Speedup**: ~2.6x faster with sophisticated parallel processing

### State Flow

1. **Parallel Research** saves to state:
   - `news_summary` (from news pipeline)
   - `social_insights` (from social pipeline)
   - `expert_quotes` (from expert pipeline)

2. **Sequential Creation** reads from state:
   - Writer: `{news_summary}`, `{social_insights}`, `{expert_quotes}`
   - Editor: `{draft_article}`
   - Formatter: `{edited_article}`

## Learning Outcomes

After completing this tutorial, you'll understand:

- ✅ **Nested Agent Orchestration**: Sequential inside Parallel agents
- ✅ **Multi-Phase Workflows**: Parallel research + sequential creation
- ✅ **Complex State Management**: Data flow in nested architectures
- ✅ **Production Architectures**: Real-world content generation patterns
- ✅ **Performance Optimization**: Strategic parallelization for speed

## Links

- **Tutorial**: [Tutorial 06: Multi-Agent Systems][source]
- **ADK Documentation**: google.github.io/adk-docs/

---

_Built with ❤️ for the ADK community_

source: https://github.com/raphaelmansuy/adk_training/blob/main/tutorial_implementation/tutorial06/README.md