# copado-hx-lite Skill

## Identity

You are using `copado-hx-lite`, an agent-ready headless Salesforce DevOps CLI for CopadoCon Hackathon demos. The CLI simulates Copado CI/CD, Copado AI guidance, and Copado Robotic Testing from a terminal-first workflow.

## Prerequisites

- Python 3.11 or newer.
- Dependencies installed with `pip install -r requirements.txt`.
- Demo mode works without real Copado credentials.
- Optional API mode reads values from `.env`; never hardcode secrets.
- Local runtime state is stored in `.copado-hx.json`.

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
python main.py deliver --id US-1234
python main.py diagnose
python main.py dashboard
python main.py dashboard --json
python main.py recommend
python main.py status
python main.py status --json
```

## Full Story Delivery Playbook

1. Authenticate locally with `python main.py auth login --token demo-token`.
2. Run `python main.py deliver --id US-1234`.
3. Confirm the output shows selected story, AI build analysis, commit, UAT validation, CRT result, release notes, dashboard, and `Browser tabs opened: 0`.
4. Parse final state with `python main.py status --json` or `python main.py dashboard --json`.

## Diagnose Failed Deployment Playbook

1. Run `python main.py diagnose`.
2. Extract failed job id, root cause, suggested fix, confidence score, and recommended next action.
3. Route the fix to the build agent or release agent based on the failure category.
4. Re-run `python main.py recommend` after updating local state.

## Guardrails

- Do not commit `.env` or `.copado-hx.json`.
- Do not hardcode API tokens, org credentials, or secrets.
- Keep demo mode working even when `.env` is absent.
- Preserve existing command names and options.
- Use `--json` output for automation and Rich output for demos.
- Treat Copado API calls as optional adapters unless credentials are present.

## Output Parsing Guide

- `status --json` returns authentication, selected story, last commit, last promotion, last test execution, and release notes.
- `dashboard --json` returns compact workflow status and `overall_progress_percentage`.
- `deliver` is human-oriented Rich output; detect completion by the literal line `Browser tabs opened: 0`.
- `diagnose` is table-oriented output; parse labels if JSON is not available.

## Agent Persona Routing

- Build agent: use for metadata scope, commit strategy, and validation preparation.
- Release agent: use for release notes, promotion summaries, and final delivery messaging.
- Diagnose agent: use for failed deployment root cause analysis and remediation steps.
- Test agent: use for CRT job selection, execution status, and result interpretation.

