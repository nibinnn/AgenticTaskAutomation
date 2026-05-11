"""
main.py — Multi-Agent Task Automation System with Claude AI Integration
Run: ANTHROPIC_API_KEY=sk-ant-... python main.py
"""
import os
import json
from orchestrator import Orchestrator

RESET="\033[0m"; BOLD="\033[1m"; CYAN="\033[96m"; GREEN="\033[92m"
RED="\033[91m"; YELLOW="\033[93m"; BLUE="\033[94m"; GREY="\033[90m"
WHITE="\033[97m"; MAGENTA="\033[95m"

def banner():
    print(f"\n{CYAN}{BOLD}╔══════════════════════════════════════════════════════╗\n║  🤖  Multi-Agent System  ×  Claude AI Integration   ║\n╚══════════════════════════════════════════════════════╝{RESET}\n")

def section(t):
    print(f"\n{BLUE}{BOLD}{'─'*54}{RESET}\n{BOLD}{WHITE}  {t}{RESET}\n{BLUE}{'─'*54}{RESET}")

def print_result(name, result, agent_name=""):
    icon = f"{GREEN}✓{RESET}" if result.success else f"{RED}✗{RESET}"
    tag  = f"{GREY}[{agent_name}]{RESET} " if agent_name else ""
    print(f"\n  {icon} {tag}{BOLD}{name}{RESET}  {GREY}⏱ {result.duration:.2f}s{RESET}")
    if result.success:
        out = result.output
        out_str = json.dumps(out, indent=2) if isinstance(out, (dict, list)) else str(out)
        for line in out_str.split("\n")[:10]:
            print(f"    {GREY}{line}{RESET}")
    else:
        print(f"    {RED}Error: {result.error}{RESET}")

def main():
    banner()
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print(f"  {YELLOW}⚠  ANTHROPIC_API_KEY not set — AI tasks will error.{RESET}")
        print(f"  {GREY}   Export: export ANTHROPIC_API_KEY='sk-ant-...'{RESET}\n")

    orc = Orchestrator(api_key=api_key)
    sales_data = [
        {"product": "Widget A", "region": "North", "revenue": 1200, "units": 40},
        {"product": "Widget B", "region": "South", "revenue": 3400, "units": 110},
        {"product": "Widget C", "region": "North", "revenue": 2100, "units": 75},
        {"product": "Widget B", "region": "North", "revenue": 4800, "units": 160},
    ]

    section("Demo A · AIAgent — Pure AI Tasks")
    ai_tasks = [
        {"name": "Fermi Reasoning",   "task_type": "reason",    "question": "How many piano tuners are in Chicago? Show your reasoning."},
        {"name": "Summarize Text",    "task_type": "summarize", "text": "AI has rapidly advanced in the past decade, with LLMs achieving human-level performance on many benchmarks. They can generate text, answer questions, write code, and reason. However, they hallucinate, show bias, and struggle with long-range planning. Researchers work on alignment to make them safer.", "depth": "brief"},
        {"name": "Extract Entities",  "task_type": "extract",   "text": "Alice Johnson (CEO) signed a $4.2M deal with Acme Corp on March 15, 2024 in New York.", "fields": ["person", "role", "company", "amount", "date", "location"]},
        {"name": "Classify Sentiment","task_type": "classify",  "text": "The product quality was outstanding, though delivery took longer than expected.", "categories": ["positive", "negative", "mixed", "neutral"]},
        {"name": "Generate Code",     "task_type": "code_gen",  "description": "Python function that retries a callable up to N times with exponential backoff", "language": "python"},
        {"name": "Plan 90-day Launch","task_type": "plan",       "goal": "Launch a B2B SaaS product in 90 days", "constraints": "Solo founder, $5k budget"},
    ]
    for t in ai_tasks:
        t["agent"] = "AIAgent"
        print_result(t["name"], orc.run_task(t), "AIAgent")

    section("Demo B · Hybrid Pipeline — Data + AI")
    pipeline = [
        {"name": "Analyze Sales",    "task_type": "analyze",    "agent": "DataAgent",    "operation": "analyze",    "data": sales_data},
        {"name": "AI: Interpret",    "task_type": "reason",     "agent": "AIAgent",       "question": f"Sales data:\n{json.dumps(sales_data, indent=2)}\n\nGive 2 insights and 1 action.", "max_tokens": 200},
        {"name": "Convert to CSV",   "task_type": "json_to_csv","agent": "TransformAgent","operation": "json_to_csv","data": sales_data},
        {"name": "Save Report",      "task_type": "write",      "agent": "FileAgent",     "operation": "write",      "filename": "sales.csv", "inject_output": True},
    ]
    results = orc.run_pipeline(pipeline)
    print()
    for r in results:
        icon = f"{GREEN}✓{RESET}" if r["success"] else f"{RED}✗{RESET}"
        print(f"  Step {r['step']:02d}  {icon}  {BOLD}{r['name']:<30}{RESET}  {GREY}[{r['agent']}]  {r['duration']:.2f}s{RESET}")
    passed = sum(1 for r in results if r["success"])
    print(f"\n  {GREEN}{BOLD}{passed}/{len(results)} steps succeeded{RESET}")

    section("System Status · All Agents")
    for name, info in orc.status_report()["agents"].items():
        color = GREEN if info["status"] == "success" else (RED if info["status"] == "failed" else GREY)
        print(f"\n  {BOLD}{MAGENTA}{name}{RESET}  {color}●{RESET} {info['status']}")
        print(f"    {GREY}{info['description']}{RESET}")
        if info["total"] > 0:
            print(f"    {GREEN}{info['success']} ok{RESET} / {RED}{info['failed']} failed{RESET}  |  avg {GREY}{info['avg_duration']:.2f}s{RESET}")

    print(f"\n{CYAN}{BOLD}  ✅ Complete!{RESET}\n")

if __name__ == "__main__":
    main()
