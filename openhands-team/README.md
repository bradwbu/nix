# OpenHands Parallel AI Development Team

A small, staged orchestrator for up to three OpenHands Software Agent SDK coding workers. It uses a separate Git worktree/branch per task, validates task boundaries before setup, and keeps integration/release under human control.

## Current state

This is the **initial scaffold**: task-contract validation, dependency ordering, clean-repository checks, and safe worktree preparation are implemented and covered by standard-library tests. It does not yet launch workers, merge branches, or release anything. The SDK smoke test is intentionally the next gate, before enabling agent execution.

## Requirements and local environment note

- Python 3.12+ for the current OpenHands SDK release.
- Git.
- For an isolated agent runtime, Docker and a working Docker daemon; the intended SDK path is `DockerWorkspace`/agent-server, not a local terminal on the host.
- One Azure AI Foundry deployment that supports the OpenAI-compatible v1 API, plus its endpoint, deployment name, and API key.

At scaffold time the official `openhands-sdk`, `openhands-tools`, `openhands-workspace`, and `openhands-agent-server` packages are all pinned to 1.54.0 and installed together to keep versions aligned. `requirements.txt` should be changed only after a new SDK version is checked and the smoke test passes.

The current development host had Python 3.11.2 and no Python 3.12 executable, so the SDK cannot be installed/run here yet. The pure validation tests run on Python 3.11.

## Setup

Create a dedicated Python 3.12 environment; do not install these dependencies into OpenClaw's Python environment:

```bash
cd openhands-team
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Set credentials through a secret manager or the calling process environment. Never put keys in `.env` committed to Git, command arguments, task files, logs, or shell history:

```text
LLM_MODEL=openai/<YOUR_FOUNDRY_DEPLOYMENT_NAME>
LLM_BASE_URL=https://<YOUR_RESOURCE>.openai.azure.com/openai/v1/
LLM_API_KEY=<provided securely at runtime>
```

The model prefix and v1 endpoint combination still need a real one-agent smoke test against the exact deployment. Azure deployments vary; do not infer compatibility from a successful config parse.

## Validate tasks

```bash
python team.py validate tasks.example.json
python -m unittest discover -s tests -v
```

Task JSON has explicit allowed paths, acceptance criteria, and dependencies. Test commands are deliberately **not** read from tasks. Configure a small, reviewed command allowlist in the future runner instead.

## Prepare isolated worktrees

```bash
python team.py prepare --repo /absolute/path/to/clean/repository \
  --tasks tasks.example.json --base main
```

This records one base commit and creates one branch/worktree per task outside the target repository. It refuses dirty repositories, overlapping path ownership, invalid dependencies, and pre-existing destination paths. If setup partially fails, it preserves created worktrees and reports them; it will not silently delete user data.

## Safety boundary

Git worktrees isolate edits and commits, **not operating-system access**. OpenHands `LocalWorkspace` executes commands on the host. Worker execution must wait until the Docker/remote workspace path is proven, with network/secret exposure minimized. Never point an agent at an untrusted repository using a host-local workspace. No automated push, merge to the base branch, or deployment is in scope.

## Staged rollout

1. Validate SDK/Python/Docker setup and run one disposable-repository SDK smoke test.
2. Implement one worker in one worktree; independently verify Git state and commit.
3. Add three-worker concurrency only after the one-worker path is reliable.
4. Add dependency-ordered integration branch merges and configured quality gates.
5. Add reviewed task planning and usage/time/conflict metrics.

The critical metric is elapsed time to a correct, tested feature—not worker count.

## References checked

- [OpenHands SDK Getting Started](https://docs.openhands.dev/sdk/getting-started)
- [OpenHands SDK LLM configuration](https://docs.openhands.dev/sdk/arch/llm)
- [OpenHands Docker sandbox guide](https://docs.openhands.dev/sdk/guides/agent-server/docker-sandbox)
- [Microsoft Foundry OpenAI v1 API](https://learn.microsoft.com/en-us/azure/foundry/openai/latest)
