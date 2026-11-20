---
name: project-board-sync
description: Keep a project's plan in step with the work - read the project board (a PROJECT_BOARD.md file, or a board tool if one is connected) before starting, then at the end suggest which steps are done, with evidence, and what new tasks, waiting-ons and decisions came up. Use at the start and end of work on a project that has a board, or when the user says "sync the board".
---

# project-board-sync

A habit, written down: look at where the project stands before working on it, and leave the plan accurate when you stop. Claude only suggests. The owner accepts each change, so the board stays theirs.

The board is `PROJECT_BOARD.md` at the repo root (template in `templates/`), planned as phases of steps, plus tasks, waiting-ons, decisions, ideas and notes. If the user has a project-board tool connected (an MCP server or similar) with list, read and propose actions, use that instead and follow the same rules.

## At the start

1. Find the board. If there is none and the user wants one, copy the template and fill it in with them. Do not invent phases.
2. Read it and note: the current phase, its open steps, open tasks, waiting-ons, decisions, and suggestions still waiting under "Suggested by Claude".
3. Say in one line which phase and step this session moves forward. If the request fits no step, say that too.

## At the end (or when the user says "sync the board")

Add one dated block under "Suggested by Claude" with only what this session established:

- **Close step:** steps that are done and verified, using the exact step text, each with its evidence (commit, PR, deploy, a check that passed). Never close a step on intent or partial work.
- **Add step:** new planned work that belongs in a phase.
- **Add task:** concrete follow-ups.
- **Waiting on:** things blocked on someone, with who was asked.
- **Decision:** choices only the owner can make, with the options.
- **Idea:** things worth considering later.
- **Note:** a short line on what changed and why, when useful.

Every item gets a one-line reason. Then tell the user in one line how many suggestions are waiting.

## Rules

- Never edit the board above "Suggested by Claude" yourself. The owner moves accepted items.
- Never suggest reopening a step. If a step looks wrongly closed, tell the user in chat.
- If the owner rejected a suggestion, do not reword it and file it again.
- No suggestions without real work behind them, and no repeats of ones still waiting.
- If you cannot write to the board, list the suggestions in chat so the owner can apply them by hand.

## Example suggestion block

```
### 2026-11-20 session
- Close step: "Contact form saves submissions" (evidence: PR #42 merged, test row visible in staging table)
- Add task: Remove the test rows tagged source='release-test' from staging
- Waiting on: Logo files in SVG (asked of: client, 2026-11-20)
- Decision: Email provider for the newsletter (options: free tier now / paid at launch)
```
