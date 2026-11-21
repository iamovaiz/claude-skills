# project-board-sync: Claude reads the plan first and leaves it accurate

Long projects drift. Claude finishes work that was never on the plan, or a step gets marked done because it was started. This skill sets one habit: read the board before working, and at the end suggest changes with evidence. You accept them; Claude never edits your plan directly.

## How it works

1. Copy `templates/PROJECT_BOARD.md` to your repo root: phases of steps, tasks, waiting-ons, decisions, ideas, notes.
2. At the start of a session Claude names the phase and step the work moves forward, or says the request fits none.
3. At the end it adds a dated block under "Suggested by Claude":

```
### 2026-11-20 session
- Close step: "Contact form saves submissions" (evidence: PR #42 merged, test row visible in staging table)
- Add task: Remove the test rows tagged source='release-test' from staging
- Waiting on: Logo files in SVG (asked of: client, 2026-11-20)
- Decision: Email provider for the newsletter (options: free tier now / paid at launch)
```

4. You move what you accept into the board and delete the rest.

## Rules Claude follows

No closing a step without evidence. No reopening steps. No re-filing a suggestion you rejected. If you have a project-board tool connected (an MCP server), it uses that instead of the file, with the same rules.
