---
id: 002
title: Add .env security constraint
stage: constitution
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["security", "constitution", "ai-agents"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - No tests required (documentation update)
---

## Prompt

```text
### Security Constraints:
- ***Do not read my .env file.*** Only .env.example is allowed to read and update.
```

## Response snapshot

Updated project constitution to version 1.0.1 with explicit security constraint for AI agents:

**Modified Section**: Security & Hardening → API Key Management
- Added: "**CRITICAL**: AI agents MUST NOT read `.env` files - only `.env.example` is allowed for reference"

**Version Bump**: 1.0.0 → 1.0.1 (PATCH)
- Rationale: Clarification to existing security principles, not a new principle or breaking change

**Impact**:
- Prevents AI agents from accidentally exposing secrets during development
- Maintains alignment with existing security practices (no template updates needed)
- Explicit constraint makes security boundary clear for autonomous agents

## Outcome

- ✅ Impact: PATCH-level constitutional amendment restricting AI agent access to .env files
- 🧪 Tests: N/A (documentation/governance update)
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: None required (complete)
- 🧠 Reflection: Security constraint now codified in constitution for all AI agents working on the project

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (governance update)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
