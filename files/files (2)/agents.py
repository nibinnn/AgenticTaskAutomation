"""
AutoAgent - AI Task Automation System
A multi-agent system for managing tasks, emails, and calendar using Claude API.
"""

import anthropic
import json
import re
from datetime import datetime, timedelta
from typing import Any
from dataclasses import dataclass, field, asdict
from enum import Enum


# ─────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AgentType(str, Enum):
    TASK = "TaskBot"
    MAIL = "MailBot"
    CAL = "CalBot"
    ORCHESTRATOR = "Orchestrator"


@dataclass
class Task:
    id: int
    title: str
    priority: Priority
    due: str
    done: bool = False
    ai_created: bool = False
    tags: list[str] = field(default_factory=list)

    def mark_done(self):
        self.done = True

    def __str__(self):
        status = "✓" if self.done else "○"
        prio_icons = {Priority.HIGH: "🔴", Priority.MEDIUM: "🟡", Priority.LOW: "⚪"}
        return f"  {status} [{prio_icons[self.priority]}] {self.title} (due: {self.due})"


@dataclass
class Email:
    id: int
    sender: str
    subject: str
    preview: str
    timestamp: str
    unread: bool = True
    urgent: bool = False
    ai_draft: str | None = None


@dataclass
class CalendarEvent:
    title: str
    date: str
    time: str
    duration_mins: int
    attendees: list[str] = field(default_factory=list)
    location: str = "Video call"
    ai_scheduled: bool = False

    def __str__(self):
        att = f" · {len(self.attendees)} attendees" if self.attendees else ""
        return f"  📅 {self.date} {self.time} — {self.title}{att} [{self.location}]"


@dataclass
class AgentResult:
    agent: AgentType
    action: str
    output: str
    data: Any = None


# ─────────────────────────────────────────────
# In-Memory State (simulated data store)
# ─────────────────────────────────────────────

TASKS: list[Task] = [
    Task(1, "Review Q2 budget proposal", Priority.HIGH, "Today", tags=["finance"]),
    Task(2, "Sign off on partnership proposal", Priority.HIGH, "Today", tags=["partnerships"]),
    Task(3, "Prepare product review slides", Priority.MEDIUM, "Today 2 PM", tags=["product"]),
    Task(4, "Send weekly digest to leadership", Priority.MEDIUM, "Today 5 PM", tags=["management"]),
    Task(5, "Review PRs from engineering", Priority.LOW, "Today", tags=["engineering"]),
    Task(6, "Update project roadmap", Priority.LOW, "No deadline", done=True, tags=["product"]),
]

EMAILS: list[Email] = [
    Email(1, "Sarah Chen", "Q2 Budget Review — needs sign-off",
          "Hi Jamie, the finance team needs your approval by EOD...", "8:14 AM", urgent=True),
    Email(2, "Alex Torres", "Re: Partnership proposal",
          "Thanks for the quick response! Could we schedule a call...", "7:52 AM",
          ai_draft="Hi Alex, I'd be happy to schedule a call. How does Thursday 2 PM work for you?"),
    Email(3, "Notion", "Your weekly summary",
          "Here's what happened in your workspace...", "6:01 AM", unread=False),
]

EVENTS: list[CalendarEvent] = [
    CalendarEvent("Team standup", "Today", "9:00 AM", 30, ["Alice", "Bob", "Carol", "Dave"]),
    CalendarEvent("Product review", "Today", "10:30 AM", 60, ["Sarah", "Mike"], "Conference room B"),
    CalendarEvent("1:1 with Sarah", "Today", "2:00 PM", 30, ["Sarah"], ai_scheduled=True),
]

NEXT_TASK_ID = len(TASKS) + 1


# ─────────────────────────────────────────────
# Tool Definitions (for Claude's tool_use)
# ─────────────────────────────────────────────

TOOLS = [
    {
        "name": "list_tasks",
        "description": "List all tasks, optionally filtered by status or priority.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "enum": ["all", "pending", "done", "high_priority"],
                    "description": "Filter tasks by status or priority"
                }
            },
            "required": []
        }
    },
    {
        "name": "create_task",
        "description": "Create a new task and add it to the task list.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The task title"},
                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                "due": {"type": "string", "description": "Due date/time as a string, e.g. 'Tomorrow 3 PM'"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional tags"}
            },
            "required": ["title", "priority", "due"]
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "The task ID to mark as done"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "list_emails",
        "description": "List emails, optionally filtered to unread or urgent only.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "enum": ["all", "unread", "urgent"],
                    "description": "Filter emails"
                }
            },
            "required": []
        }
    },
    {
        "name": "draft_email_reply",
        "description": "Draft a reply to an email. Returns the drafted reply text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {"type": "integer", "description": "The email ID to reply to"},
                "tone": {
                    "type": "string",
                    "enum": ["formal", "friendly", "concise"],
                    "description": "Tone of the reply"
                },
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key points to include in the reply"
                }
            },
            "required": ["email_id"]
        }
    },
    {
        "name": "list_calendar",
        "description": "List upcoming calendar events.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days_ahead": {
                    "type": "integer",
                    "description": "How many days ahead to look (default 7)"
                }
            },
            "required": []
        }
    },
    {
        "name": "find_meeting_slot",
        "description": "Find available time slots for a meeting next week, avoiding conflicts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "duration_mins": {
                    "type": "integer",
                    "description": "Duration of the meeting in minutes"
                },
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of attendee names"
                },
                "preferred_time": {
                    "type": "string",
                    "description": "Preferred time of day: morning, afternoon, or any"
                }
            },
            "required": ["duration_mins"]
        }
    },
    {
        "name": "schedule_meeting",
        "description": "Schedule a new meeting on the calendar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "date": {"type": "string"},
                "time": {"type": "string"},
                "duration_mins": {"type": "integer"},
                "attendees": {"type": "array", "items": {"type": "string"}},
                "location": {"type": "string"}
            },
            "required": ["title", "date", "time", "duration_mins"]
        }
    },
    {
        "name": "get_daily_summary",
        "description": "Get a comprehensive summary of today's tasks, emails, and meetings.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


# ─────────────────────────────────────────────
# Tool Executor
# ─────────────────────────────────────────────

def execute_tool(name: str, inputs: dict) -> dict:
    """Route tool calls to the appropriate handler."""
    global NEXT_TASK_ID

    if name == "list_tasks":
        f = inputs.get("filter", "all")
        filtered = TASKS
        if f == "pending":
            filtered = [t for t in TASKS if not t.done]
        elif f == "done":
            filtered = [t for t in TASKS if t.done]
        elif f == "high_priority":
            filtered = [t for t in TASKS if t.priority == Priority.HIGH and not t.done]
        return {
            "tasks": [asdict(t) for t in filtered],
            "count": len(filtered)
        }

    elif name == "create_task":
        task = Task(
            id=NEXT_TASK_ID,
            title=inputs["title"],
            priority=Priority(inputs["priority"]),
            due=inputs.get("due", "No deadline"),
            ai_created=True,
            tags=inputs.get("tags", [])
        )
        TASKS.append(task)
        NEXT_TASK_ID += 1
        return {"created": asdict(task), "message": f"Task #{task.id} created: '{task.title}'"}

    elif name == "complete_task":
        tid = inputs["task_id"]
        task = next((t for t in TASKS if t.id == tid), None)
        if task:
            task.mark_done()
            return {"success": True, "message": f"Task #{tid} '{task.title}' marked as done."}
        return {"success": False, "message": f"Task #{tid} not found."}

    elif name == "list_emails":
        f = inputs.get("filter", "all")
        filtered = EMAILS
        if f == "unread":
            filtered = [e for e in EMAILS if e.unread]
        elif f == "urgent":
            filtered = [e for e in EMAILS if e.urgent]
        return {
            "emails": [asdict(e) for e in filtered],
            "count": len(filtered)
        }

    elif name == "draft_email_reply":
        eid = inputs["email_id"]
        email = next((e for e in EMAILS if e.id == eid), None)
        if not email:
            return {"success": False, "message": f"Email #{eid} not found."}
        tone = inputs.get("tone", "friendly")
        points = inputs.get("key_points", [])
        draft = email.ai_draft or f"Hi {email.sender.split()[0]},\n\nThank you for reaching out. {' '.join(points)}\n\nBest regards,\nJamie"
        email.ai_draft = draft
        return {"success": True, "draft": draft, "tone": tone, "email_subject": email.subject}

    elif name == "list_calendar":
        days = inputs.get("days_ahead", 7)
        return {
            "events": [asdict(e) for e in EVENTS],
            "days_ahead": days,
            "count": len(EVENTS)
        }

    elif name == "find_meeting_slot":
        duration = inputs.get("duration_mins", 60)
        preferred = inputs.get("preferred_time", "any")
        attendees = inputs.get("attendees", ["Team"])

        # Simulate finding open slots next week
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        slots = []
        time_ranges = {
            "morning": [("9:00 AM", 9), ("10:00 AM", 10), ("11:00 AM", 11)],
            "afternoon": [("1:00 PM", 13), ("2:00 PM", 14), ("3:00 PM", 15)],
            "any": [("9:00 AM", 9), ("11:00 AM", 11), ("2:00 PM", 14)],
        }
        times = time_ranges.get(preferred, time_ranges["any"])

        for i, (day_offset, day_name) in enumerate([
            (0, "Monday"), (1, "Tuesday"), (2, "Wednesday")
        ]):
            day = next_monday + timedelta(days=day_offset)
            t_str, t_hour = times[i % len(times)]
            end_hour = t_hour + duration // 60
            end_min = duration % 60
            end_str = f"{end_hour}:{end_min:02d} {'AM' if end_hour < 12 else 'PM'}"
            slots.append({
                "date": day.strftime("%A, %B %d"),
                "time": t_str,
                "end_time": end_str,
                "available": True,
                "conflicts": []
            })

        return {
            "available_slots": slots,
            "duration_mins": duration,
            "attendees": attendees,
            "recommendation": slots[0]
        }

    elif name == "schedule_meeting":
        event = CalendarEvent(
            title=inputs["title"],
            date=inputs["date"],
            time=inputs["time"],
            duration_mins=inputs["duration_mins"],
            attendees=inputs.get("attendees", []),
            location=inputs.get("location", "Video call"),
            ai_scheduled=True
        )
        EVENTS.append(event)
        return {
            "success": True,
            "event": asdict(event),
            "message": f"Meeting '{event.title}' scheduled for {event.date} at {event.time}."
        }

    elif name == "get_daily_summary":
        pending = [t for t in TASKS if not t.done]
        urgent_emails = [e for e in EMAILS if e.urgent and e.unread]
        return {
            "date": datetime.now().strftime("%A, %B %d %Y"),
            "tasks": {"total": len(TASKS), "pending": len(pending), "done": len(TASKS) - len(pending)},
            "emails": {"total": len(EMAILS), "unread": sum(1 for e in EMAILS if e.unread), "urgent": len(urgent_emails)},
            "meetings": {"count": len(EVENTS), "events": [e.title for e in EVENTS]},
            "high_priority_tasks": [t.title for t in pending if t.priority == Priority.HIGH]
        }

    return {"error": f"Unknown tool: {name}"}


# ─────────────────────────────────────────────
# Agentic Loop
# ─────────────────────────────────────────────

class AutoAgent:
    def __init__(self, verbose: bool = True):
        self.client = anthropic.Anthropic()
        self.verbose = verbose
        self.history: list[dict] = []
        self.activity_log: list[str] = []
        self.system_prompt = """You are AutoAgent, an AI productivity assistant managing tasks, emails, and calendar for a busy professional named Jamie.

You have access to tools for:
- TaskBot capabilities: list tasks, create tasks, complete tasks
- MailBot capabilities: list emails, draft email replies
- CalBot capabilities: list calendar events, find meeting slots, schedule meetings
- get_daily_summary: gives a full overview

When given a command:
1. Analyze what needs to be done
2. Use the appropriate tools — you can chain multiple tool calls
3. After all tool calls, summarize what you did in a clear, concise message

Always be proactive: if asked to schedule a meeting, also find the best slot first. If asked to handle emails, check for urgent ones. Be specific with times, dates, and names in your final response.

Today is """ + datetime.now().strftime("%A, %B %d, %Y") + "."

    def _log(self, agent: str, message: str):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] [{agent}] {message}"
        self.activity_log.append(entry)
        if self.verbose:
            colors = {
                "TaskBot": "\033[94m",   # blue
                "MailBot": "\033[92m",   # green
                "CalBot": "\033[96m",    # cyan
                "Orchestrator": "\033[93m",  # yellow
                "System": "\033[90m",    # gray
            }
            color = colors.get(agent, "\033[0m")
            print(f"{color}{entry}\033[0m")

    def run(self, user_input: str) -> str:
        """Execute one turn of the agentic loop with tool use."""
        self._log("Orchestrator", f"Received command: '{user_input}'")
        self.history.append({"role": "user", "content": user_input})

        messages = self.history.copy()
        final_response = ""

        # Agentic loop — keep going until no more tool calls
        while True:
            response = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=4096,
                system=self.system_prompt,
                tools=TOOLS,
                messages=messages
            )

            # Collect text and tool use from this response
            tool_calls = []
            text_parts = []

            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_calls.append(block)

            # Add assistant message to conversation
            messages.append({"role": "assistant", "content": response.content})

            if not tool_calls:
                # No more tools — we're done
                final_response = " ".join(text_parts)
                break

            # Execute each tool call
            tool_results = []
            for tc in tool_calls:
                tool_name = tc.name
                tool_input = tc.input

                # Determine which agent handles this tool
                agent_map = {
                    "list_tasks": AgentType.TASK, "create_task": AgentType.TASK, "complete_task": AgentType.TASK,
                    "list_emails": AgentType.MAIL, "draft_email_reply": AgentType.MAIL,
                    "list_calendar": AgentType.CAL, "find_meeting_slot": AgentType.CAL, "schedule_meeting": AgentType.CAL,
                    "get_daily_summary": AgentType.ORCHESTRATOR,
                }
                agent = agent_map.get(tool_name, AgentType.ORCHESTRATOR)
                self._log(agent.value, f"Calling tool: {tool_name}({json.dumps(tool_input, indent=None)})")

                result = execute_tool(tool_name, tool_input)
                self._log(agent.value, f"Tool result: {json.dumps(result)[:120]}{'...' if len(json.dumps(result)) > 120 else ''}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": json.dumps(result)
                })

            # Feed results back into the conversation
            messages.append({"role": "user", "content": tool_results})

        # Save final exchange to persistent history
        self.history.append({"role": "assistant", "content": final_response})
        return final_response

    def print_state(self):
        """Print current state of all data stores."""
        print("\n" + "═" * 60)
        print("📋  TASKS")
        print("═" * 60)
        for t in TASKS:
            print(t)

        print("\n" + "═" * 60)
        print("✉️   EMAILS")
        print("═" * 60)
        for e in EMAILS:
            status = "🔴 URGENT" if e.urgent else ("📬 UNREAD" if e.unread else "📭 READ")
            print(f"  {status} | From: {e.sender} | {e.subject}")

        print("\n" + "═" * 60)
        print("📅  CALENDAR")
        print("═" * 60)
        for ev in EVENTS:
            print(ev)

        print("\n" + "═" * 60)
        print("📝  ACTIVITY LOG")
        print("═" * 60)
        for entry in self.activity_log[-10:]:
            print(f"  {entry}")
        print()


# ─────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────

def print_banner():
    print("\033[96m")
    print("╔══════════════════════════════════════════════════╗")
    print("║          🤖  AutoAgent — Task Automation          ║")
    print("║     TaskBot · MailBot · CalBot · Orchestrator     ║")
    print("╚══════════════════════════════════════════════════╝")
    print("\033[0m")
    print("Commands: type naturally, or use:")
    print("  \033[93m/state\033[0m  — show current tasks, emails, calendar")
    print("  \033[93m/log\033[0m    — show agent activity log")
    print("  \033[93m/quit\033[0m   — exit")
    print()


def main():
    print_banner()
    agent = AutoAgent(verbose=True)

    # Run a default greeting summary on startup
    print("\033[90m[Initializing agents...]\033[0m\n")
    greeting = agent.run("Give me a daily summary and tell me what needs my attention most urgently.")
    print(f"\n\033[1m🤖 AutoAgent:\033[0m {greeting}\n")
    print("─" * 60)

    while True:
        try:
            user_input = input("\n\033[1mYou:\033[0m ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\033[90mGoodbye!\033[0m")
            break

        if not user_input:
            continue

        if user_input.lower() == "/quit":
            print("\033[90mGoodbye!\033[0m")
            break
        elif user_input.lower() == "/state":
            agent.print_state()
            continue
        elif user_input.lower() == "/log":
            print("\n".join(agent.activity_log[-20:]))
            continue

        print()
        response = agent.run(user_input)
        print(f"\n\033[1m🤖 AutoAgent:\033[0m {response}")
        print("\n" + "─" * 60)


if __name__ == "__main__":
    main()
