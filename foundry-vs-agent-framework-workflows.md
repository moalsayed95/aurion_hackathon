# Foundry Workflows vs. Agent Framework SDK Workflows

## What Are We Comparing?

Microsoft offers **two ways** to build workflows in the Foundry ecosystem. They serve different audiences and have very different capabilities.

| | Foundry Declarative Workflows | Agent Framework SDK Workflows |
|---|---|---|
| **What it is** | Visual/YAML workflow builder in the Foundry portal | Python (or C#) code using the `agent-framework` package |
| **Who it's for** | Business users, citizen developers, low-code scenarios | Professional developers building complex agentic systems |
| **Where you build** | Foundry portal UI or VS Code YAML editor | Python IDE, VS Code, any code editor |
| **How you deploy** | Saved in Foundry portal (versioned) | Containerized, deployed to Foundry Agent Service |

---

## Foundry Declarative Workflows — What They Are

Built in the **Foundry portal** at ai.azure.com via a **visual drag-and-drop builder**. You connect nodes to define a flow. Under the hood, it's YAML.

### Available Node Types

| Node | What It Does |
|------|-------------|
| **Invoke Agent** | Call a Foundry agent (existing or new, inline) |
| **If / Else** | Conditional branching |
| **For Each** | Loop over a collection |
| **Go To** | Jump to another node |
| **Set Variable** | Store a value for later use |
| **Parse Value** | Extract data from agent output |
| **Send Message** | Send a message to the user |
| **Ask a Question** | Collect user input (with options) |

### Logic & Expressions

Uses **Power Fx** (Excel-like formula language) for conditions and transformations:
```
If(Local.category == "claim", "Process claim", "General inquiry")
Concat("Hello ", Local.customerName, "!")
IsBlank(Local.policyNumber)
```

### Variables

- `System.Activity` — current incoming message
- `System.LastMessage.Text` — last user message
- `Local.*` — workflow-scoped variables you define
- `Conversation.*` — conversation metadata

### What's Good About Them

- **Very fast to prototype** — drag, drop, connect, done
- **No code required** — accessible to non-developers
- **Versioned** — every save creates an immutable version
- **Agent integration** — invoke any Foundry agent, configure structured JSON output
- **Logic Apps connectors** — attach Azure Logic Apps as agent actions, giving access to 1,400+ external service connectors (email, CRM, databases, etc.)
- **Convertible** — Foundry portal + GitHub Copilot can convert YAML workflows to Agent Framework Python/C# code

### What's Limited

- **Fixed action set** — you can only use the node types above; no custom logic beyond Power Fx
- **No parallel execution** — steps run sequentially; no fan-out/fan-in
- **No streaming** — results only available after workflow completes
- **No checkpointing** — if it fails midway, start over
- **No stateful executors** — no persistent state between steps beyond simple variables
- **No sub-workflow composition** — can't nest workflows inside workflows
- **Simple routing only** — if/else and switch, but no multi-target conditional fan-out
- **No middleware** — can't intercept or transform at the framework level
- **Power Fx limitations** — no complex types, limited function library compared to Python

---

## Agent Framework SDK Workflows — What They Are

Python code using `WorkflowBuilder`, `Executor`, `@handler`, and orchestration builders (`SequentialBuilder`, `ConcurrentBuilder`, `HandoffBuilder`, `GroupChatBuilder`, `MagenticBuilder`).

You define executors (nodes), connect them with edges (optionally conditional), and run the workflow. Full Python available everywhere.

### What's Good About Them

- **Full Python** — any library, any logic, any integration, anywhere in the flow
- **5 orchestration patterns** built-in (Sequential, Concurrent, Handoff, Group Chat, Magentic)
- **Streaming** — real-time event stream during execution (`executor_invoked`, `output`, `request_info`, etc.)
- **Stateful executors** — classes with persistent internal state + checkpoint save/restore hooks
- **Checkpointing & resume** — pause, persist, resume later (even across process restarts)
- **Human-in-the-loop** — `ctx.request_info()` pauses for human input, `@response_handler` processes the response
- **Fan-out / fan-in** — parallel execution with synchronized aggregation
- **Conditional routing** — edge conditions, switch/case with default, multi-target selection
- **Sub-workflows** — nest workflows inside workflows, intercept child requests from parent
- **Middleware** — agent, function, and chat middleware for cross-cutting concerns (security, logging, audit)
- **Strong typing** — Pydantic models, dataclasses, Python types with auto-validation
- **Testable** — standard Python testing, mock agents, in-memory storage, event inspection
- **Debuggable** — Python debugger, breakpoints, log inspection, event observation

### What's More Work

- **Requires Python skills** — not accessible to non-developers
- **More setup** — project structure, dependencies, deployment config
- **Single-process** — executors run in one Python process (horizontal scaling needs custom infra)
- **Steeper learning curve** — more concepts to learn (executors, handlers, contexts, edges, builders)

---

## Side-by-Side Comparison

| Capability | Foundry Declarative | Agent Framework SDK |
|---|---|---|
| **Build experience** | Visual drag-and-drop | Python code |
| **Time to first demo** | Minutes | Hours |
| **Custom logic** | Power Fx formulas only | Full Python |
| **Agent invocation** | Yes (Foundry agents) | Yes (any LLM client) |
| **Conditional routing** | If/else, switch | Edge conditions, switch/case, multi-target |
| **Parallel execution** | No | Yes (fan-out/fan-in, concurrent orchestration) |
| **Streaming events** | No | Yes (real-time token-level) |
| **Stateful nodes** | Variables only | Full executor state + checkpoint lifecycle |
| **Checkpointing** | No | Yes (automatic at superstep boundaries) |
| **Human-in-the-loop** | Ask a Question node | request_info + response_handler + checkpoint resume |
| **Sub-workflows** | No | Yes (WorkflowExecutor with request interception) |
| **Middleware** | No | Agent, function, and chat middleware |
| **Loops** | For Each, Go To | Self-edges, feedback loops with conditions |
| **Error handling** | Limited | Try/catch in Python, middleware error handling |
| **Testing** | Portal playground | Python unit tests, mock agents, event inspection |
| **Debugging** | Portal logs | Python debugger, breakpoints, OpenTelemetry |
| **External connectors** | Logic Apps (1,400+ connectors) | Python libraries (aiohttp, SDKs, etc.) |
| **Deployment** | Foundry portal | Containerized → Foundry Agent Service |
| **Type system** | JSON Schema | Python types, Pydantic models |
| **Observability** | Portal-based | OpenTelemetry, custom event handlers |
| **Version control** | Portal versioning | Git |

---

## Why the Agent Framework SDK Is the Right Choice for This Hackathon

### 1. Our flow needs parallel and conditional logic

The claim intake workflow has conditional routing (claim vs. inquiry vs. complaint → different paths) and could benefit from parallel extraction (extract data while classifying). Foundry declarative workflows can't do parallel execution and have limited conditional routing.

### 2. We need rich document processing

Azure Document Intelligence returns complex structured data (tables, key-value pairs, paragraphs). Processing this requires real Python logic — parsing, transforming, validating — not Power Fx formulas.

### 3. Human-in-the-loop with state

When a high-value claim needs human approval, we want the workflow to pause, persist its state, and resume after the human decides. The SDK's `request_info` + checkpointing makes this clean. Foundry's "Ask a Question" is limited to simple user input.

### 4. We want streaming for the demo

Showing real-time token streaming as agents think and respond is far more impressive in a hackathon demo than waiting for a complete result. The SDK gives us event-by-event streaming.

### 5. Multi-agent orchestration patterns

We may want Handoff (triage → specialist routing) or Sequential (pipeline of extraction → classification → decision). The SDK gives us 5 pre-built orchestration patterns. Foundry declarative workflows only support linear step-by-step flows.

### 6. Testability and iteration speed

During the hackathon, we'll iterate fast. Python code with unit tests and a debugger beats editing YAML in a portal and hoping it works.

### 7. It's what Aurion can build on

After the hackathon, Aurion's development team can extend the Python codebase, add new agents, integrate with their systems, and deploy to production. A Foundry declarative workflow would hit limitations quickly as requirements grow.

---

## When Would Foundry Declarative Workflows Be Better?

They have their place:

- **Quick prototypes** — if you just need "call agent A, then agent B" with no complex logic
- **Non-developer users** — business analysts who want to wire up existing agents
- **Logic Apps integration** — if you need to connect to 1,400+ services (Outlook, SAP, Dynamics, etc.) without code
- **Simple approval flows** — basic "ask user, branch on answer" scenarios

For anything beyond that — and our hackathon use case is definitely beyond that — the Agent Framework SDK is the way to go.

---

## The Bridge: Converting Between Them

Microsoft provides a path from declarative → code:

- In the Foundry portal, you can view any workflow as YAML
- Using VS Code + GitHub Copilot, you can convert that YAML to Agent Framework Python or C# code
- The SDK also has a `agent-framework-declarative` package that can run YAML workflows from Python

So you're not locked in. You could prototype in the portal, then convert to code when you need more power. But for a hackathon where we want to showcase the full capabilities, starting with code is the right call.
