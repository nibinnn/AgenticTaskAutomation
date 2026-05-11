import { useState, useRef } from "react";

const AGENT_MANIFEST = {
  DataAgent: { color: "#1D9E75", bg: "#E1F5EE", ops: ["analyze","filter","sort","aggregate","summarize","validate"], desc: "Structured data analysis" },
  TransformAgent: { color: "#BA7517", bg: "#FAEEDA", ops: ["json_to_csv","flatten","encode","template","extract"], desc: "Format conversion" },
  FileAgent: { color: "#378ADD", bg: "#E6F1FB", ops: ["write","read","list","delete","checksum"], desc: "File I/O operations" },
  SchedulerAgent: { color: "#D4537E", bg: "#FBEAF0", ops: ["schedule","chain"], desc: "Task scheduling" },
  AIAgent: { color: "#7F77DD", bg: "#EEEDFE", ops: ["reason","summarize","extract","classify","code_gen","generate","plan","critique"], desc: "Claude LLM intelligence" },
};

const SAMPLE_DATA = [
  { product: "Widget A", region: "North", revenue: 1200, units: 40 },
  { product: "Widget B", region: "South", revenue: 3400, units: 110 },
  { product: "Widget C", region: "North", revenue: 2100, units: 75 },
  { product: "Widget B", region: "North", revenue: 4800, units: 160 },
  { product: "Widget A", region: "East",  revenue: 680,  units: 22 },
];

const EXAMPLES = [
  { label: "Sales Intelligence", req: "Analyze my sales data to find top-performing products by revenue, then have AI summarize the key business insights, and save the results as a CSV file." },
  { label: "Feedback Analysis", req: "Classify the customer feedback as positive, negative, or neutral. Then generate an executive summary report of overall sentiment patterns." },
  { label: "Code + Review", req: "Generate a Python class for a rate limiter with token bucket algorithm. Then critique the generated code for correctness and edge cases." },
  { label: "ETL Pipeline", req: "Filter my sales data to only records with revenue above 1500, convert to CSV format, then encode it as base64 for secure transmission." },
];

const SYSTEM_PROMPT = `You are a workflow planning AI for a multi-agent automation system.
Read the user's requirement and design the optimal pipeline of tasks.

Available agents:
- DataAgent: analyze, filter, sort, aggregate, summarize, validate (needs: data array, operation, optional condition/key)
- TransformAgent: json_to_csv, flatten, encode, template, extract (needs: data or text, operation)
- FileAgent: write, read, list (needs: filename, content or operation)
- AIAgent: reason, summarize, extract, classify, code_gen, generate, plan, critique (needs: question/text/description/topic/goal/content)
- SchedulerAgent: schedule, chain

Return ONLY a JSON object:
{
  "goal_summary": "one sentence",
  "reasoning": "2-3 sentences explaining your choices",
  "pipeline": [
    {
      "step": 1,
      "name": "Short name",
      "agent": "AgentName",
      "task_type": "operation",
      "operation": "operation",
      "description": "what this step does",
      "inject_output": false,
      ... relevant fields (data, text, question, filename, condition, key, etc.)
    }
  ]
}

Rules:
- inject_output: true means previous step's output feeds into this step
- For AIAgent reason: use "question" field. For summarize: use "text". For code_gen: "description" + "language". For classify: "text" + "categories". For generate: "topic". For plan: "goal". For critique: "content".
- For DataAgent filter: add condition: {field, op (gt/lt/eq/contains), value}
- For DataAgent sort: add key (field name), reverse (bool)  
- For DataAgent aggregate: add group_by (field name)
- For TransformAgent encode: add text + method (base64/hex/url)
- For TransformAgent template: add template (string with {{var}}) + variables (dict)
- For TransformAgent extract: add text + pattern (regex)
- For FileAgent write: add filename + content (or inject_output:true)
- If user provides data, embed the actual data array in step "data" field for DataAgent/TransformAgent
- Return ONLY the JSON. No markdown, no explanation outside JSON.`;

function AgentBadge({ name }) {
  const a = AGENT_MANIFEST[name] || { color: "#888", bg: "#f0f0f0" };
  return (
    <span style={{ fontSize: 11, fontWeight: 500, padding: "2px 7px", borderRadius: 100, background: a.bg, color: a.color, whiteSpace: "nowrap" }}>
      {name}
    </span>
  );
}

function StepCard({ step, result, isRunning }) {
  const agent = AGENT_MANIFEST[step.agent] || {};
  const status = result ? (result.success ? "ok" : "error") : isRunning ? "running" : "pending";
  const statusColor = { ok: "#1D9E75", error: "#A32D2D", running: "#BA7517", pending: "#888" }[status];
  const statusLabel = { ok: "✓", error: "✗", running: "…", pending: "·" }[status];

  return (
    <div style={{ display: "flex", gap: 12, padding: "10px 0", borderBottom: "0.5px solid var(--color-border-tertiary)" }}>
      <div style={{ width: 28, height: 28, borderRadius: "50%", background: agent.bg || "#f0f0f0", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 600, color: agent.color || "#888", flexShrink: 0, marginTop: 1 }}>
        {statusLabel}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          <span style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-primary)" }}>{step.name}</span>
          <AgentBadge name={step.agent} />
          <span style={{ fontSize: 11, color: "var(--color-text-secondary)" }}>{step.task_type}</span>
          {result && <span style={{ fontSize: 11, color: "var(--color-text-tertiary)", marginLeft: "auto" }}>{result.duration?.toFixed(2)}s</span>}
        </div>
        <div style={{ fontSize: 12, color: "var(--color-text-secondary)", marginTop: 2 }}>{step.description}</div>
        {result && !result.success && (
          <div style={{ fontSize: 12, color: "#A32D2D", marginTop: 4, background: "#FCEBEB", padding: "4px 8px", borderRadius: 4 }}>
            {result.error}
          </div>
        )}
        {result?.success && result.output !== null && result.output !== undefined && (
          <div style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--color-text-secondary)", marginTop: 4, maxHeight: 80, overflow: "hidden", background: "var(--color-background-secondary)", padding: "4px 8px", borderRadius: 4 }}>
            {typeof result.output === "object" ? JSON.stringify(result.output, null, 2).slice(0, 300) : String(result.output).slice(0, 300)}
            {(typeof result.output === "object" ? JSON.stringify(result.output) : String(result.output)).length > 300 ? "…" : ""}
          </div>
        )}
      </div>
    </div>
  );
}

// Simulate local execution for non-AI agents
function executeLocally(step, prevOutput, contextData) {
  const op = step.operation || step.task_type;
  let data = step.data ?? (step.inject_output && prevOutput !== null ? prevOutput : null);
  if (!data && contextData) data = contextData;

  try {
    if (step.agent === "DataAgent") {
      if (!Array.isArray(data)) return { success: false, output: null, error: "DataAgent needs an array. Provide data in context.", duration: 0 };
      if (op === "analyze") {
        const numFields = {};
        data.forEach(r => Object.entries(r).forEach(([k, v]) => { if (typeof v === "number") { numFields[k] = numFields[k] || []; numFields[k].push(v); } }));
        const stats = {};
        Object.entries(numFields).forEach(([k, vals]) => { stats[k] = { min: Math.min(...vals), max: Math.max(...vals), mean: +(vals.reduce((a,b)=>a+b,0)/vals.length).toFixed(2), count: vals.length }; });
        return { success: true, output: { record_count: data.length, field_stats: stats }, duration: 0.001 };
      }
      if (op === "filter") {
        const c = step.condition || {};
        const filtered = data.filter(r => {
          const v = r[c.field]; if (v === undefined) return false;
          if (c.op === "gt") return v > c.value;
          if (c.op === "lt") return v < c.value;
          if (c.op === "eq") return v === c.value;
          if (c.op === "contains") return String(v).includes(c.value);
          return false;
        });
        return { success: true, output: filtered, duration: 0.001 };
      }
      if (op === "sort") {
        const key = step.key || Object.keys(data[0]).find(k => typeof data[0][k] === "number");
        const sorted = [...data].sort((a, b) => step.reverse ? b[key] - a[key] : a[key] - b[key]);
        return { success: true, output: sorted, duration: 0.001 };
      }
      if (op === "aggregate") {
        const groups = {};
        data.forEach(r => { const k = r[step.group_by] || "unknown"; groups[k] = (groups[k] || 0) + 1; });
        return { success: true, output: groups, duration: 0.001 };
      }
      if (op === "summarize") return { success: true, output: { total: data.length, fields: Object.keys(data[0] || {}), sample: data.slice(0, 2) }, duration: 0.001 };
      if (op === "validate") {
        const schema = step.schema || {};
        const errors = [];
        data.forEach((row, i) => {
          Object.entries(schema).forEach(([field, rules]) => {
            if (rules.required && !(field in row)) errors.push(`Row ${i}: missing '${field}'`);
          });
        });
        return { success: true, output: { valid: errors.length === 0, errors, checked: data.length }, duration: 0.001 };
      }
    }

    if (step.agent === "TransformAgent") {
      const inputData = step.inject_output && prevOutput !== null ? prevOutput : (step.data || data);
      if (op === "json_to_csv") {
        const arr = Array.isArray(inputData) ? inputData : data;
        if (!arr?.length) return { success: false, output: null, error: "Need array data", duration: 0 };
        const keys = Object.keys(arr[0]);
        const rows = arr.map(r => keys.map(k => JSON.stringify(r[k] ?? "")).join(","));
        return { success: true, output: [keys.join(","), ...rows].join("\n"), duration: 0.001 };
      }
      if (op === "flatten") {
        const obj = typeof inputData === "object" ? inputData : {};
        function flat(o, prefix = "", sep = ".") {
          return Object.entries(o).reduce((acc, [k, v]) => {
            const key = prefix ? `${prefix}${sep}${k}` : k;
            if (v && typeof v === "object" && !Array.isArray(v)) Object.assign(acc, flat(v, key, sep));
            else acc[key] = v;
            return acc;
          }, {});
        }
        return { success: true, output: flat(obj), duration: 0.001 };
      }
      if (op === "encode") {
        const text = step.text || String(inputData);
        const method = step.method || "base64";
        let encoded = method === "base64" ? btoa(unescape(encodeURIComponent(text))) : method === "url" ? encodeURIComponent(text) : text.split("").map(c => c.charCodeAt(0).toString(16)).join("");
        return { success: true, output: { original: text.slice(0, 50), encoded: encoded.slice(0, 100), method }, duration: 0.001 };
      }
      if (op === "template") {
        const vars = step.variables || {};
        const result = (step.template || "").replace(/\{\{(\w+)\}\}/g, (_, k) => vars[k] || `{{${k}}}`);
        return { success: true, output: result, duration: 0.001 };
      }
      if (op === "extract") {
        const text = step.text || String(inputData || "");
        try { const matches = text.match(new RegExp(step.pattern || ".", "g")) || []; return { success: true, output: matches, duration: 0.001 }; }
        catch (e) { return { success: false, output: null, error: "Invalid regex: " + e.message, duration: 0 }; }
      }
    }

    if (step.agent === "FileAgent") {
      const content = step.inject_output && prevOutput !== null
        ? (typeof prevOutput === "string" ? prevOutput : JSON.stringify(prevOutput, null, 2))
        : step.content;
      if (op === "write") return { success: true, output: { path: `/tmp/${step.filename}`, bytes: (content || "").length, written: true }, duration: 0.001 };
      if (op === "list") return { success: true, output: [{ name: "example.txt", size: 128 }], duration: 0.001 };
      if (op === "read") return { success: true, output: { filename: step.filename, content: "(simulated file content)", lines: 5 }, duration: 0.001 };
    }

    if (step.agent === "SchedulerAgent") {
      return { success: true, output: { queued: true, queue_length: 1, priority: step.priority || 5 }, duration: 0.001 };
    }

    return { success: false, output: null, error: `Cannot execute ${step.agent}/${op} locally`, duration: 0 };
  } catch (e) {
    return { success: false, output: null, error: e.message, duration: 0 };
  }
}

export default function App() {
  const [apiKey, setApiKey] = useState("");
  const [keyVisible, setKeyVisible] = useState(false);
  const [requirement, setRequirement] = useState("");
  const [contextJson, setContextJson] = useState(JSON.stringify(SAMPLE_DATA, null, 2));
  const [showContext, setShowContext] = useState(false);
  const [phase, setPhase] = useState("idle"); // idle | planning | executing | done | error
  const [plan, setPlan] = useState(null);
  const [stepResults, setStepResults] = useState([]);
  const [runningStep, setRunningStep] = useState(-1);
  const [finalOutput, setFinalOutput] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [showFinal, setShowFinal] = useState(false);
  const abortRef = useRef(false);

  async function callClaude(messages, system, maxTokens = 2048) {
    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-api-key": apiKey, "anthropic-version": "2023-06-01" },
      body: JSON.stringify({ model: "claude-sonnet-4-20250514", max_tokens: maxTokens, system, messages }),
    });
    if (!resp.ok) { const e = await resp.json().catch(() => ({})); throw new Error(e.error?.message || resp.statusText); }
    const data = await resp.json();
    return (data.content || []).filter(b => b.type === "text").map(b => b.text).join("\n").trim();
  }

  async function run() {
    if (!apiKey) { setErrorMsg("Enter your Anthropic API key first."); setPhase("error"); return; }
    if (!requirement.trim()) { setErrorMsg("Enter a requirement first."); setPhase("error"); return; }
    abortRef.current = false;
    setPhase("planning"); setPlan(null); setStepResults([]); setFinalOutput(null); setErrorMsg(""); setShowFinal(false);

    let contextData = null;
    try { if (contextJson.trim()) contextData = JSON.parse(contextJson); } catch (_) {}

    // ── Phase 1: Plan ─────────────────────────────────────────────────────
    let planObj;
    try {
      const userMsg = `Requirement: ${requirement}\n\nContext data available: ${contextData ? "Yes — array of " + (Array.isArray(contextData) ? contextData.length : "?") + " records with fields: " + (Array.isArray(contextData) && contextData[0] ? Object.keys(contextData[0]).join(", ") : "unknown") : "None provided"}`;
      const raw = await callClaude([{ role: "user", content: userMsg }], SYSTEM_PROMPT, 2048);
      const cleaned = raw.replace(/^```(?:json)?\s*|\s*```$/gm, "").trim();
      planObj = JSON.parse(cleaned);
    } catch (e) {
      setErrorMsg("Planning failed: " + e.message); setPhase("error"); return;
    }

    if (!planObj.pipeline?.length) { setErrorMsg("AI returned an empty pipeline."); setPhase("error"); return; }
    setPlan(planObj);
    setPhase("executing");

    // ── Phase 2: Execute ──────────────────────────────────────────────────
    const results = [];
    let prevOutput = null;

    for (let i = 0; i < planObj.pipeline.length; i++) {
      if (abortRef.current) break;
      const step = planObj.pipeline[i];
      setRunningStep(i);

      let result;
      const t0 = performance.now();

      if (step.agent === "AIAgent") {
        // Call Claude for AI steps
        try {
          const op = step.task_type || step.operation;
          const injectText = step.inject_output && prevOutput !== null
            ? "\n\nPrevious step output:\n" + (typeof prevOutput === "object" ? JSON.stringify(prevOutput, null, 2) : prevOutput)
            : "";

          const promptMap = {
            reason: (step.question || step.prompt || "") + injectText,
            summarize: `Summarize briefly:\n\n${step.text || injectText}`,
            extract: `Extract key entities from this text and return ONLY valid JSON:\n\n${step.text || injectText}`,
            classify: `Classify this text. Return JSON: {"category": "...", "confidence": 0.0, "reasoning": "..."}.\nCategories: ${(step.categories || ["positive","negative","neutral"]).join(", ")}\n\nText: ${step.text || injectText}`,
            code_gen: `Write clean ${step.language || "python"} code for:\n${step.description || ""}\n\nReturn only the code.`,
            generate: `Write about: ${step.topic || ""}`,
            plan: `Break this into actionable steps:\n${step.goal || ""}`,
            critique: `Critique this for quality, correctness, edge cases:\n\n${step.content || injectText}`,
          };
          const sysMap = {
            reason: "You are a precise reasoning assistant.", summarize: "You summarize concisely.",
            extract: "You extract structured data. Return only valid JSON.", classify: "You classify text. Return only JSON.",
            code_gen: "You write clean production code. Return code only.", generate: "You are a skilled writer.",
            plan: "You create clear actionable plans.", critique: "You give constructive, specific critique.",
          };
          const text = await callClaude([{ role: "user", content: promptMap[op] || (step.question || step.prompt || "") }], sysMap[op] || "You are a helpful assistant.", step.max_tokens || 1024);
          let output = text;
          try { const c = text.replace(/^```(?:json)?\s*|\s*```$/gm, "").trim(); output = JSON.parse(c); } catch (_) {}
          result = { success: true, output, error: null, duration: (performance.now() - t0) / 1000 };
        } catch (e) {
          result = { success: false, output: null, error: e.message, duration: (performance.now() - t0) / 1000 };
        }
      } else {
        // Execute locally for non-AI agents
        result = executeLocally(step, prevOutput, Array.isArray(contextData) ? contextData : null);
        result.duration = (performance.now() - t0) / 1000;
      }

      if (result.success) prevOutput = result.output;
      results.push({ ...step, ...result });
      setStepResults([...results]);
    }

    setRunningStep(-1);
    setFinalOutput(prevOutput);
    setPhase("done");
  }

  const agentCounts = plan ? plan.pipeline.reduce((acc, s) => { acc[s.agent] = (acc[s.agent] || 0) + 1; return acc; }, {}) : {};

  return (
    <div style={{ padding: "1.25rem 0", fontFamily: "var(--font-sans)" }}>

      {/* Header */}
      <div style={{ marginBottom: "1.25rem" }}>
        <h2 style={{ fontSize: 16, fontWeight: 500, margin: "0 0 4px" }}>AI Pipeline Generator</h2>
        <p style={{ fontSize: 13, color: "var(--color-text-secondary)", margin: 0 }}>Describe what you want in plain English. AI designs and runs the pipeline.</p>
      </div>

      {/* API Key */}
      <div style={{ marginBottom: "0.75rem" }}>
        <label style={{ fontSize: 12, color: "var(--color-text-secondary)", display: "block", marginBottom: 4 }}>Anthropic API key</label>
        <div style={{ display: "flex", gap: 6 }}>
          <input type={keyVisible ? "text" : "password"} value={apiKey} onChange={e => setApiKey(e.target.value)}
            placeholder="sk-ant-api03-..." style={{ flex: 1, fontSize: 13 }} />
          <button onClick={() => setKeyVisible(v => !v)}
            style={{ fontSize: 12, padding: "0 12px", background: "var(--color-background-secondary)", border: "0.5px solid var(--color-border-secondary)", borderRadius: "var(--border-radius-md)", cursor: "pointer", color: "var(--color-text-secondary)" }}>
            {keyVisible ? "hide" : "show"}
          </button>
        </div>
      </div>

      {/* Example pills */}
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: "0.75rem" }}>
        {EXAMPLES.map(ex => (
          <button key={ex.label} onClick={() => setRequirement(ex.req)}
            style={{ fontSize: 12, padding: "4px 10px", borderRadius: 100, border: "0.5px solid var(--color-border-secondary)", background: "var(--color-background-secondary)", color: "var(--color-text-secondary)", cursor: "pointer" }}>
            {ex.label}
          </button>
        ))}
      </div>

      {/* Requirement input */}
      <div style={{ marginBottom: "0.75rem" }}>
        <label style={{ fontSize: 12, color: "var(--color-text-secondary)", display: "block", marginBottom: 4 }}>Your requirement</label>
        <textarea value={requirement} onChange={e => setRequirement(e.target.value)}
          placeholder="e.g. Analyze my sales data, find top products by revenue, summarize insights with AI, and save as CSV..."
          style={{ width: "100%", minHeight: 72, fontSize: 13, lineHeight: 1.5, resize: "vertical" }} />
      </div>

      {/* Context data (collapsible) */}
      <div style={{ marginBottom: "1rem" }}>
        <button onClick={() => setShowContext(v => !v)}
          style={{ fontSize: 12, color: "var(--color-text-secondary)", background: "none", border: "none", cursor: "pointer", padding: 0, display: "flex", alignItems: "center", gap: 4 }}>
          <span style={{ fontSize: 10 }}>{showContext ? "▼" : "▶"}</span> Context data (JSON) — used by DataAgent steps
        </button>
        {showContext && (
          <textarea value={contextJson} onChange={e => setContextJson(e.target.value)}
            style={{ width: "100%", minHeight: 100, fontSize: 11, fontFamily: "var(--font-mono)", marginTop: 6, resize: "vertical" }} />
        )}
      </div>

      {/* Run button */}
      <button onClick={run} disabled={phase === "planning" || phase === "executing"}
        style={{ width: "100%", padding: "9px 0", fontSize: 13, fontWeight: 500, background: "#7F77DD", color: "#EEEDFE", border: "none", borderRadius: "var(--border-radius-md)", cursor: phase === "planning" || phase === "executing" ? "not-allowed" : "pointer", opacity: phase === "planning" || phase === "executing" ? 0.6 : 1 }}>
        {phase === "planning" ? "🧠 Planning pipeline…" : phase === "executing" ? "⚙️ Executing…" : "Generate & Run Pipeline →"}
      </button>

      {/* Error */}
      {phase === "error" && (
        <div style={{ marginTop: "0.75rem", padding: "8px 12px", background: "#FCEBEB", border: "0.5px solid rgba(162,45,45,.3)", borderRadius: "var(--border-radius-md)", fontSize: 13, color: "#A32D2D" }}>{errorMsg}</div>
      )}

      {/* Plan */}
      {plan && (
        <div style={{ marginTop: "1.25rem" }}>
          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12, marginBottom: "0.75rem" }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-primary)", marginBottom: 2 }}>🧠 {plan.goal_summary}</div>
              <div style={{ fontSize: 12, color: "var(--color-text-secondary)" }}>{plan.reasoning}</div>
            </div>
            <div style={{ display: "flex", gap: 4, flexShrink: 0, flexWrap: "wrap", justifyContent: "flex-end" }}>
              {Object.entries(agentCounts).map(([name, count]) => (
                <AgentBadge key={name} name={name} />
              ))}
            </div>
          </div>

          <div style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-lg)", border: "0.5px solid var(--color-border-tertiary)", padding: "0.25rem 1rem" }}>
            {plan.pipeline.map((step, i) => (
              <StepCard key={i} step={step} result={stepResults[i] || null} isRunning={runningStep === i} />
            ))}
          </div>
        </div>
      )}

      {/* Final output */}
      {phase === "done" && finalOutput !== null && (
        <div style={{ marginTop: "1rem" }}>
          <button onClick={() => setShowFinal(v => !v)}
            style={{ fontSize: 12, color: "var(--color-text-secondary)", background: "none", border: "none", cursor: "pointer", padding: 0, display: "flex", alignItems: "center", gap: 4, marginBottom: 6 }}>
            <span style={{ fontSize: 10 }}>{showFinal ? "▼" : "▶"}</span> Final output
          </button>
          {showFinal && (
            <pre style={{ fontSize: 11, fontFamily: "var(--font-mono)", background: "var(--color-background-secondary)", padding: "10px 12px", borderRadius: "var(--border-radius-md)", border: "0.5px solid var(--color-border-tertiary)", overflow: "auto", maxHeight: 240, color: "var(--color-text-primary)", whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {typeof finalOutput === "object" ? JSON.stringify(finalOutput, null, 2) : String(finalOutput)}
            </pre>
          )}
        </div>
      )}

      {/* Done summary */}
      {phase === "done" && (
        <div style={{ marginTop: "0.75rem", display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 12, color: "#1D9E75", fontWeight: 500 }}>
            ✓ {stepResults.filter(r => r.success).length}/{stepResults.length} steps succeeded
          </span>
          <button onClick={() => { setPhase("idle"); setPlan(null); setStepResults([]); setFinalOutput(null); }}
            style={{ fontSize: 12, padding: "3px 10px", borderRadius: 100, border: "0.5px solid var(--color-border-secondary)", background: "none", cursor: "pointer", color: "var(--color-text-secondary)" }}>
            Reset
          </button>
        </div>
      )}
    </div>
  );
}
