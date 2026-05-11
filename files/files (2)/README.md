# AutoAgent — AI Task Automation System

A multi-agent Python system using the Claude API to manage **tasks**, **emails**, and **calendar** through natural language commands.

---

## Architecture

```
User Input
    │
    ▼
Orchestrator (Claude claude-opus-4-6)
    │  ← decides which tools to call
    ├── TaskBot  → list_tasks, create_task, complete_task
    ├── MailBot  → list_emails, draft_email_reply
    └── CalBot   → list_calendar, find_meeting_slot, schedule_meeting
```

The system uses **Claude's tool_use (function calling)** in an agentic loop — Claude decides which tools to call, sees the results, and can chain multiple calls before giving a final response.

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 3. Run
python agents.py
```

---

## Example Commands

```
You: Give me a summary of today
You: Find time for a team meeting next week
You: Create a high-priority task to review the Q3 report, due tomorrow
You: Draft a reply to email #2 in a friendly tone
You: Mark task 3 as done
You: What urgent emails do I have?
You: Schedule a 1-hour product sync on Wednesday at 2 PM with Alice and Bob
You: Show me my calendar for the week
```

## CLI Commands

| Command  | Description                          |
|----------|--------------------------------------|
| `/state` | Print current tasks, emails, calendar |
| `/log`   | Show the agent activity log           |
| `/quit`  | Exit the program                      |

---

## How It Works

1. Your message is sent to Claude with a set of **tool definitions**
2. Claude decides which tools to call (can be multiple in one turn)
3. Tools execute against the in-memory data store and return results
4. Claude sees the results, may call more tools, then writes a final reply
5. The full conversation history is maintained for context across turns

## Extending

To add a new agent capability:
1. Add a tool definition to the `TOOLS` list
2. Add a handler in `execute_tool()`
3. Map the tool name to an `AgentType` in `agent_map` inside `AutoAgent.run()`
