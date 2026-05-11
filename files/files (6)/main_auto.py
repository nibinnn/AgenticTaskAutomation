"""
main_auto.py — AI-Generated Pipeline Demo
=========================================
The user describes what they want. The system figures out how to do it.

Run:
    ANTHROPIC_API_KEY=sk-ant-... python main_auto.py
"""
import os
import json
from auto_orchestrator import AutoOrchestrator

RESET="\033[0m"; BOLD="\033[1m"; CYAN="\033[96m"; GREEN="\033[92m"
RED="\033[91m"; YELLOW="\033[93m"; BLUE="\033[94m"; GREY="\033[90m"
WHITE="\033[97m"; MAGENTA="\033[95m"


def banner():
    print(f"""
{CYAN}{BOLD}
╔══════════════════════════════════════════════════════════════╗
║   🧠  AutoOrchestrator — AI-Generated Pipeline Engine        ║
║       Describe what you want. AI builds & runs the workflow. ║
╚══════════════════════════════════════════════════════════════╝
{RESET}""")


def divider(title=""):
    print(f"\n{BLUE}{BOLD}{'═'*62}{RESET}")
    if title:
        print(f"{BOLD}{WHITE}  {title}{RESET}")
    print(f"{BLUE}{'═'*62}{RESET}\n")


def show_pipeline(pipeline: list):
    """Pretty-print the AI-generated pipeline before execution."""
    print(f"  {MAGENTA}{BOLD}Generated Pipeline:{RESET}")
    for step in pipeline:
        print(f"  {GREY}Step {step.get('step', '?'):02d}{RESET}  "
              f"{BOLD}{step.get('name', '?'):<35}{RESET}  "
              f"{CYAN}[{step.get('agent', '?')}]{RESET}  "
              f"{GREY}{step.get('task_type', '')} · {step.get('description', '')[:60]}{RESET}")
    print()


def show_final(result: dict):
    """Show the final output from the pipeline."""
    out = result.get("final_output")
    if out is None:
        return
    print(f"\n  {BOLD}Final output:{RESET}")
    out_str = json.dumps(out, indent=2) if isinstance(out, (dict, list)) else str(out)
    for line in out_str.split("\n")[:20]:
        print(f"    {GREY}{line}{RESET}")
    if out_str.count("\n") >= 20:
        print(f"    {GREY}...{RESET}")


# ── Sample data ────────────────────────────────────────────────────────────────

SALES_DATA = [
    {"product": "Widget A", "region": "North", "revenue": 1200, "units": 40, "quarter": "Q1"},
    {"product": "Widget B", "region": "South", "revenue": 3400, "units": 110, "quarter": "Q1"},
    {"product": "Widget A", "region": "South", "revenue": 950,  "units": 30,  "quarter": "Q2"},
    {"product": "Widget C", "region": "North", "revenue": 2100, "units": 75,  "quarter": "Q1"},
    {"product": "Widget B", "region": "North", "revenue": 4800, "units": 160, "quarter": "Q2"},
    {"product": "Widget C", "region": "East",  "revenue": 1750, "units": 60,  "quarter": "Q2"},
    {"product": "Widget A", "region": "East",  "revenue": 680,  "units": 22,  "quarter": "Q1"},
]

CUSTOMER_FEEDBACK = """
Customer #1: The onboarding experience was smooth and the UI is very intuitive. Loved it!
Customer #2: Terrible support. Waited 3 days for a response and the issue still isn't resolved.
Customer #3: Product works as advertised but the pricing feels steep compared to competitors.
Customer #4: Amazing product! Best purchase I've made this year. Highly recommend.
Customer #5: The new dashboard feature is confusing. I couldn't find where to export my data.
Customer #6: Fast, reliable, and the team is very responsive. 5 stars!
Customer #7: Had a billing problem that took two weeks to fix. Very frustrating experience.
"""


def main():
    banner()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print(f"  {RED}✗ ANTHROPIC_API_KEY not set.{RESET}")
        print(f"  {GREY}  Export: export ANTHROPIC_API_KEY='sk-ant-...'{RESET}\n")
        return

    orc = AutoOrchestrator(api_key=api_key)

    # ══ Requirement 1 ═══════════════════════════════════════════════════════════
    divider("Requirement 1 · Sales Intelligence")
    req1 = (
        "I have sales data for multiple products and regions. "
        "Analyze it to find top-performing products by revenue, "
        "then have AI summarize the key business insights, "
        "and finally save the top products as a CSV file."
    )
    print(f"  {YELLOW}Requirement:{RESET} {req1}\n")
    result1 = orc.solve(req1, context={"data": SALES_DATA})
    show_pipeline(result1["pipeline"])
    show_final(result1)

    # ══ Requirement 2 ═══════════════════════════════════════════════════════════
    divider("Requirement 2 · Customer Feedback Analysis")
    req2 = (
        "I have customer feedback text. "
        "Classify each piece of feedback as positive, negative, or neutral. "
        "Then generate an executive summary report of the overall sentiment, "
        "and write that report to a file called feedback_report.txt."
    )
    print(f"  {YELLOW}Requirement:{RESET} {req2}\n")
    result2 = orc.solve(req2, context={"feedback_text": CUSTOMER_FEEDBACK})
    show_pipeline(result2["pipeline"])
    show_final(result2)

    # ══ Requirement 3 ═══════════════════════════════════════════════════════════
    divider("Requirement 3 · Code Generation + Review")
    req3 = (
        "Generate a Python class for a rate limiter with token bucket algorithm. "
        "Then critique the generated code for correctness and edge cases. "
        "Save both the code and the critique to separate files."
    )
    print(f"  {YELLOW}Requirement:{RESET} {req3}\n")
    result3 = orc.solve(req3)
    show_pipeline(result3["pipeline"])
    show_final(result3)

    # ══ Requirement 4 ═══════════════════════════════════════════════════════════
    divider("Requirement 4 · Data Validation + Transform")
    req4 = (
        "Validate my sales data against a schema (product:str required, revenue:int required), "
        "filter out records with revenue below 1500, "
        "convert the remaining records to CSV format, "
        "and encode the CSV as base64 for transmission."
    )
    print(f"  {YELLOW}Requirement:{RESET} {req4}\n")
    result4 = orc.solve(req4, context={"data": SALES_DATA})
    show_pipeline(result4["pipeline"])
    show_final(result4)

    # ══ Summary ═════════════════════════════════════════════════════════════════
    divider("System Summary")
    status = orc.status()
    for name, info in status.items():
        color = GREEN if info["status"] == "success" else (RED if info["status"] == "failed" else GREY)
        tasks_str = f"{GREEN}{info['success']} ok{RESET}/{RED}{info['failed']} fail{RESET}" if info["total"] else f"{GREY}idle{RESET}"
        print(f"  {MAGENTA}{BOLD}{name:<20}{RESET}  {color}●{RESET} {tasks_str}")

    print(f"\n{CYAN}{BOLD}  ✅ All requirements processed.{RESET}\n")


if __name__ == "__main__":
    main()
