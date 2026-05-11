#!/bin/bash
set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   🤖  Multi-Agent Task Automation System                     ║"
echo "║       FastAPI · Python · Claude AI · Docker                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

check_api_key() {
  if [ -z "${ANTHROPIC_API_KEY}" ]; then
    echo "⚠  ANTHROPIC_API_KEY not set — AI endpoints will return errors."
    echo "   Pass: -e ANTHROPIC_API_KEY=sk-ant-..."
    echo ""
  else
    echo "✓  API key detected (${ANTHROPIC_API_KEY:0:12}...)"
    echo ""
  fi
}

HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-8000}"
WORKERS="${API_WORKERS:-1}"

case "$1" in

  api|"")
    check_api_key
    echo "▶  Starting FastAPI server on http://${HOST}:${PORT}"
    echo "   Docs: http://localhost:${PORT}/docs"
    echo ""
    exec uvicorn app:app \
      --host "${HOST}" \
      --port "${PORT}" \
      --workers "${WORKERS}" \
      --log-level "${LOG_LEVEL,,}"
    ;;

  api-dev)
    check_api_key
    echo "▶  Starting FastAPI in DEV mode (hot-reload) on http://${HOST}:${PORT}"
    echo ""
    exec uvicorn app:app \
      --host "${HOST}" \
      --port "${PORT}" \
      --reload \
      --log-level debug
    ;;

  demo)
    check_api_key
    echo "▶  Running manual pipeline demo (main.py)..."
    exec python main.py
    ;;

  auto)
    check_api_key
    echo "▶  Running AI-generated pipeline demo (main_auto.py)..."
    exec python main_auto.py
    ;;

  solve)
    check_api_key
    if [ -z "${REQUIREMENT}" ]; then
      echo "❌  REQUIREMENT env var not set."
      exit 1
    fi
    echo "▶  Solving: ${REQUIREMENT}"
    exec python -c "
import os, json
from auto_orchestrator import AutoOrchestrator
req = os.environ['REQUIREMENT']
ctx_raw = os.environ.get('CONTEXT_JSON', '')
context = json.loads(ctx_raw) if ctx_raw else {}
orc = AutoOrchestrator(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))
result = orc.solve(req, context=context, verbose=True)
print()
out = result.get('final_output')
print(json.dumps(out, indent=2) if isinstance(out, (dict, list)) else str(out) if out else '(no output)')
"
    ;;

  test)
    echo "▶  Running smoke tests..."
    exec python -c "
import sys
print('  Checking agent imports...')
from agents.base_agent import BaseAgent, TaskResult
from agents.specialized_agents import DataAgent, FileAgent, TransformAgent, SchedulerAgent
from agents.ai_agent import AIAgent
from agents.planner_agent import PlannerAgent
from auto_orchestrator import AutoOrchestrator
print('  ✓ Agent imports OK')

print('  Checking FastAPI app...')
from app import app
assert len(app.routes) > 20, 'Expected 20+ routes'
routes = [r.path for r in app.routes if hasattr(r, 'path')]
print(f'  ✓ FastAPI app OK — {len(routes)} routes registered')

print('  Checking non-AI agents...')
orc = AutoOrchestrator(api_key='dummy')
data = [{'x': 1, 'y': 10}, {'x': 2, 'y': 20}]
r = orc.agents['DataAgent'].run({'name':'t','task_type':'analyze','operation':'analyze','data':data})
assert r.success, r.error
r = orc.agents['TransformAgent'].run({'name':'t','task_type':'json_to_csv','operation':'json_to_csv','data':data})
assert r.success, r.error
r = orc.agents['FileAgent'].run({'name':'t','task_type':'write','operation':'write','filename':'smoke.txt','content':'hi'})
assert r.success, r.error
print('  ✓ Agent execution OK')

print()
print('  ✅ All tests passed!')
"
    ;;

  shell|bash)
    exec /bin/bash
    ;;

  python)
    shift
    exec python "$@"
    ;;

  *)
    if [ -f "$1" ]; then
      check_api_key
      exec python "$@"
    else
      echo "Commands: api (default) | api-dev | demo | auto | solve | test | shell | python <script>"
      exit 1
    fi
    ;;
esac
