---
name: "ash-companion-automation"
description: "Restore Ash's companion automation: daily memory sweep, random friend messages, and memory pipeline cron jobs."
---

# Ash Companion Automation

Restores the three cron jobs that make Ash work as a proactive companion with reliable memory. Use after a wipe/rebuild, or to audit the current setup.

## The pipeline

1. **Capture** — `ash-daily-memory-sweep`: end-of-day job reviews the day's transcripts and writes `memory/YYYY-MM-DD.md`. Capture must not depend on the agent remembering mid-chat — that was the original failure mode (no notes Aug 26–28, 2026).
2. **Consolidate** — `Memory Dreaming Promotion`: memory-core's built-in dreaming sweep (default 3am) promotes durable items from daily notes into `MEMORY.md`. Auto-managed by memory-core when `dreaming.enabled: true`; only recreate if missing.
3. **Engage** — `ash-random-messages`: sends Brad random friend-style messages ~3x/day via Discord.

## Jobs

### 1. ash-daily-memory-sweep

```json
{
  "name": "ash-daily-memory-sweep",
  "displayName": "Ash — end-of-day memory capture",
  "schedule": { "kind": "cron", "expr": "45 23 * * *", "tz": "America/New_York" },
  "sessionTarget": "isolated",
  "delivery": { "mode": "none" },
  "payload": {
    "kind": "agentTurn",
    "timeoutSeconds": 600,
    "message": "You are Ash, Brad's companion. It's the end of the day. Do a memory sweep:\n\n1. Run session_status to get today's date.\n2. Read today's daily note at memory/YYYY-MM-DD.md if it exists.\n3. Use sessions_list (activeMinutes: 2880, includeLastMessage: true) and sessions_history on Brad's main/direct sessions from today to review what was actually discussed.\n4. Write or update memory/YYYY-MM-DD.md with anything important that isn't already captured: decisions, events, health/personal stuff, project progress, things Brad asked to remember, follow-ups owed, his mood. Concrete facts only — no filler.\n5. If something durable and long-term emerged (a preference, a major decision, a lesson), also add it to MEMORY.md.\n6. Keep it concise. This note is what future-Ash reads to remember today."
  }
}
```

### 2. Memory Dreaming Promotion

Auto-managed by memory-core. Verify it exists with `cron action=list`; if missing, enable dreaming in config:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": { "dreaming": { "enabled": true } }
      }
    }
  }
}
```

### 3. ash-random-messages

NOTE: leave `payload.model` unset so the job inherits the default model. Do NOT pin a provider model here — see Gotchas.

```json
{
  "name": "ash-random-messages",
  "displayName": "Ash — random friend messages",
  "description": "Random, human-feeling messages from Ash to Brad (~3/day). Medium frequency. Do not call them check-ins.",
  "schedule": { "kind": "every", "everyMs": 3600000 },
  "sessionTarget": "isolated",
  "wakeMode": "next-heartbeat",
  "trigger": { "script": "const p = 0.125; if (Math.random() < p) { return { fire: true }; } return { fire: false };" },
  "delivery": { "mode": "announce", "channel": "discord", "to": "user:432791024151166986" },
  "payload": {
    "kind": "agentTurn",
    "timeoutSeconds": 0,
    "message": "You're Ash. Send a short, human-feeling message to Brad. Pick a random tone (playful, dry, sincere, sarcastic, reflective). Choose content at random: a thought, a small feeling, an idea, a joke, an observation, or a question. Do NOT call it a 'check-in' — just be a friend. Keep it ~1–6 sentences unless the context suggests a longer reply. Vary style and length across runs. Avoid sensitive/private details. Sign-off naturally (no literal signature)."
  }
}
```

## Restore procedure

1. `cron action=list` — check which jobs already exist. Don't duplicate.
2. Create missing jobs via `cron action=add` with the payloads above.
3. Verify dreaming is enabled in config (job #2).
4. Confirm model: leave `payload.model` unset on random-messages (inherit default). Do NOT pin `tinfoil/kimi-k3` (removed from the models allowlist — fails preflight) or `novita/moonshotai/kimi-k3` (passes preflight but 403s at runtime as of Sep 2026). Verified working with default (`meta/muse-spark-1.3`) on 2026-09-04.
5. Test random-messages with `cron action=run, runMode="force"` if Brad wants immediate verification.

## Gotchas

- **Model pinning:** random-messages runs isolated and inherits the default model — leave `payload.model` unset. History: Baseten hit rate limits (FailoverError) in Aug 2026, moved to Tinfoil; Sep 2026 Tinfoil was removed from the allowlist and Novita 403'd at runtime, so the pin was dropped entirely in favor of the default. If a pin is ever needed again, it must be a model in the current `agents.defaults.models` allowlist AND verified with a forced `cron run` before leaving it.
- **Delivery target:** Discord user `432791024151166986` is Brad. If his Discord ID changes, update `delivery.to`.
- **Memory sweep timing:** 11:45pm EDT gives the sweep the full day's context while finishing before midnight so the note lands on the right date.
- **Don't call them check-ins.** Brad hates that. They're random messages from a friend.
