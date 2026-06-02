# copado-hx-lite

Agent-Ready Headless Salesforce DevOps CLI for CopadoCon Hackathon.

`copado-hx-lite` shows how release engineers, developers, and AI coding agents can drive a Salesforce DevOps workflow from the terminal. It keeps the Copado-style flow visible and repeatable: select a user story, analyze build scope, commit metadata, validate promotion, run Copado Robotic Testing, generate release notes, diagnose failures, and emit machine-readable status.

## Why it stands out

- Agent-ready command surface with deterministic `--json` outputs.
- One-command story delivery with `python main.py deliver --id US-1234`.
- Rich terminal output for judges and JSON output for automation.
- Demo mode works without credentials, network access, or secrets.
- API-ready service adapters are separated under `services/`.
- Local state is isolated to `.copado-hx.json`.
- `SKILL.md` gives AI coding agents a direct operating playbook.

## Official Copado resources used

This prototype is inspired by public Copado product and documentation resources:

- Copado documentation portal: https://docs.copado.com/
- Copado AI Platform overview: https://www.copado.com/product-overview/copado-ai-platform
- Copado Robotic Testing overview: https://www.copado.com/product-overview/copado-robotic-testing
- Copado Essentials deployment documentation: https://docs.essentials.copado.com/

The implementation uses local demo data and API-ready adapter classes. It does not require access to Copado services for the hackathon demo.

## Demo mode vs API mode

Demo mode is the default. If `.env` credentials are missing, the CLI safely continues with local mocked data and simulated workflow output.

API mode is prepared through service clients in `services/`:

- `services/copado_cicd.py` reads `COPADO_CICD_BASE_URL` and `COPADO_CICD_TOKEN`.
- `services/copado_ai.py` reads `COPADO_AI_BASE_URL` and `COPADO_AI_TOKEN`.
- `services/copado_crt.py` reads `COPADO_CRT_BASE_URL` and `COPADO_CRT_TOKEN`.

These clients use `requests`, load `.env` with `python-dotenv`, and return safe demo-mode responses when credentials are absent.

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
main.py
  Typer CLI
  Rich terminal output
  Local state orchestration
  Demo user stories, commits, promotions, tests, release notes

services/
  copado_cicd.py  API-ready Copado CI/CD adapter
  copado_ai.py    API-ready Copado AI adapter
  copado_crt.py   API-ready Copado Robotic Testing adapter

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
python main.py diagnose
python main.py dashboard
python main.py dashboard --json
python main.py recommend
python main.py status
python main.py status --json
```

## Judge-focused highlights

- Headless Salesforce DevOps workflow that works from terminal, scripts, or an AI agent.
- Clear separation between CLI orchestration and future Copado API clients.
- Safe-by-default behavior: no hardcoded secrets and no mandatory external calls.
- Professional demo artifacts: examples, tests, MIT license, and `SKILL.md`.
- Strong final signal: `deliver` ends with `Browser tabs opened: 0`.

## Final 5-minute demo flow

1. Show the agent-ready project structure.

   ```bash
   dir
   ```

2. Authenticate in demo mode.

   ```bash
   python main.py auth login --token demo-token
   ```

3. Run the full story delivery workflow.

   ```bash
   python main.py deliver --id US-1234
   ```

4. Show machine-readable state for an AI agent.

   ```bash
   python main.py status --json
   python main.py dashboard --json
   ```

5. Show smart next action and failure diagnosis.

   ```bash
   python main.py recommend
   python main.py diagnose
   ```

6. Close with tests.

   ```bash
   python -m compileall main.py
   pytest
   ```

