# copado-hx-lite

Agent-Ready Headless Salesforce DevOps CLI built for CopadoCon 2026 Hackathon.

`copado-hx-lite` helps developers, release engineers, and AI coding agents drive a Salesforce DevOps workflow directly from the terminal. It demonstrates a Copado-style delivery flow without opening the Copado browser UI: select a user story, analyze build scope, commit metadata, validate promotion, run CRT-style tests, generate release notes, diagnose failures, and emit automation-ready JSON status.

## Why it stands out

- One-command story delivery with `python main.py deliver --id US-1234`.
- Agent-ready command surface with deterministic `--json` outputs.
- Rich terminal output for human review and JSON output for automation.
- API-ready service adapters under `services/`.
- `SKILL.md` enables AI coding agents to understand and drive the CLI.
- Safe-by-default design with no hardcoded secrets.
- Local runtime state isolated to `.copado-hx.json`.
- Demo ends with a strong measurable result: `Browser tabs opened: 0`.

## Built to match the judging criteria

### Creativity / Innovation

The project goes beyond simple CLI commands by introducing one-command delivery:

```bash
python main.py deliver --id US-1234

# copado-hx-lite

Agent-Ready Headless Salesforce DevOps CLI built for CopadoCon 2026 Hackathon.

`copado-hx-lite` helps developers, release engineers, and AI coding agents drive a Salesforce DevOps workflow directly from the terminal. It demonstrates a Copado-style delivery flow without opening the Copado browser UI: select a user story, analyze build scope, commit metadata, validate promotion, run CRT-style tests, generate release notes, diagnose failures, and emit automation-ready JSON status.

## Why it stands out

- One-command story delivery with `python main.py deliver --id US-1234`.
- Agent-ready command surface with deterministic `--json` outputs.
- Rich terminal output for human review and JSON output for automation.
- API-ready service adapters under `services/`.
- `SKILL.md` enables AI coding agents to understand and drive the CLI.
- Safe-by-default design with no hardcoded secrets.
- Local runtime state isolated to `.copado-hx.json`.
- Demo ends with a strong measurable result: `Browser tabs opened: 0`.

## Built to match the judging criteria

### Creativity / Innovation

The project goes beyond simple CLI commands by introducing one-command delivery:

```bash
python main.py deliver --id US-1234

This simulates an end-to-end Salesforce DevOps journey: story selection, AI build analysis, commit, UAT validation, CRT-style testing, release notes, dashboard summary, and zero browser tabs.

### Business Relevance

Salesforce teams often switch between IDEs, Git, Copado UI, testing tools, dashboards, and release documentation. `copado-hx-lite` reduces this context switching by moving the workflow into the terminal, making delivery faster, repeatable, and automation-friendly.

### Demo Quality

The demo is designed as a complete story, not disconnected commands. It shows a user story moving from selected work item to validated delivery with AI assistance, test results, release notes, JSON output, and failure diagnosis.

## Official Copado Resource Alignment

`copado-hx-lite` is designed around the official Copado Headless Hackathon resource areas.

| Copado Resource Area | How copado-hx-lite aligns |
|---|---|
| Copado CI/CD / Agentia Pro | User story context, commit simulation, UAT validation, promotion workflow, deployment-ready command design |
| Copado Robotic Testing / CRT | CRT-style job execution, test results, coverage summary, execution status, and automation-ready output |
| Copado AI Platform | AI-style Build Agent analysis, Release Agent notes, failure diagnosis, smart recommendations, and `SKILL.md` for agent usage |
| API Integration Resources | `services/` adapters are prepared for Copado CI/CD, Copado AI, and CRT credentials through `.env` |
| Security Requirements | No hardcoded secrets, no tokens committed, local state isolated to `.copado-hx.json` |

The current submission runs in a reliable offline demo mode so judges can evaluate the complete workflow without depending on live credentials or network setup. The codebase also includes API-ready service adapters so the same command surface can be connected to Copado Playground, Copado AI, and CRT credentials through environment variables.

## Execution Modes

### Demo Mode

Demo mode is the default execution path. It allows the full headless DevOps workflow to run locally without external credentials. This makes the demo stable, repeatable, and safe for evaluation.

### API-Ready Mode

The project includes service adapters for future live integration:

- `services/copado_cicd.py` for Copado CI/CD actions
- `services/copado_ai.py` for Copado AI agent dialogue
- `services/copado_crt.py` for Copado Robotic Testing jobs

When official hackathon credentials are configured in `.env`, these adapters can be extended to call real Copado APIs without changing the CLI command surface.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` only for real integration experiments:

```bash
copy .env.example .env
```

Do not commit `.env` or `.copado-hx.json`. Both are ignored by `.gitignore`.

## Architecture

```text
Developer / Release Engineer / AI Agent
        |
        v
main.py
  Typer CLI
  Rich terminal output
  Local workflow orchestration
  JSON automation output
        |
        v
services/
  copado_cicd.py  API-ready Copado CI/CD adapter
  copado_ai.py    API-ready Copado AI adapter
  copado_crt.py   API-ready Copado Robotic Testing adapter
        |
        v
Copado CI/CD + Copado AI + Copado CRT
```

Project structure:

```text
examples/
  demo-flow.txt
  status.example.json
  dashboard.example.json

tests/
  pytest coverage for help, JSON outputs, and delivery completion

SKILL.md
  Agent operating guide and persona routing

.copado-hx.json
  Local runtime state only
```

## Commands Reference

```bash
python main.py auth login --token demo-token
python main.py auth status
python main.py auth logout

python main.py story list
python main.py story set --id US-1234
python main.py story show

python main.py ai ask --agent build "What metadata should I commit?"
python main.py commit --message "feat: lead scoring"
python main.py promote --env UAT --validate

python main.py test list
python main.py test run --job JOB-101
python main.py test status --execution EXE-101
python main.py test results --execution EXE-101

python main.py ai ask --agent release "Generate release notes"

python main.py deliver --id US-1234
python main.py dashboard
python main.py dashboard --json
python main.py status
python main.py status --json
python main.py recommend
python main.py diagnose
```

## Key Demo Feature

```bash
python main.py deliver --id US-1234
```

This single command performs:

```text
Selected Story
AI Build Analysis
Commit Created
Promotion Validation
CRT Test Result
Release Notes
Dashboard Summary
Browser tabs opened: 0
```

## Judge-Focused Highlights

- Headless Salesforce DevOps workflow from terminal, scripts, or AI agents.
- One-command delivery instead of multiple manual UI steps.
- JSON output for automation and agent parsing.
- API-ready architecture for official Copado services.
- Safety-first design with no hardcoded credentials.
- Professional repository structure with tests, examples, MIT license, and `SKILL.md`.
- Strong business signal: reduced browser dependency and less developer context switching.

## Final 5-Minute Demo Flow

1. Show the project structure.

```bash
dir
```

2. Authenticate in demo mode.

```bash
python main.py auth login --token demo-token
```

3. Run full story delivery.

```bash
python main.py deliver --id US-1234
```

4. Show automation-ready output.

```bash
python main.py status --json
python main.py dashboard --json
```

5. Show recommendation and diagnosis.

```bash
python main.py recommend
python main.py diagnose
```

6. Show code quality checks.

```bash
python -m compileall main.py
python -m pytest
```

## Testing

```bash
python -m pytest
```

Expected result:

```text
4 passed
```

## Security

- `.env` is ignored.
- `.copado-hx.json` is ignored.
- No real API keys are stored in source code.
- Runtime state stays local.
- API credentials must be supplied only through environment variables.

## License

MIT License
