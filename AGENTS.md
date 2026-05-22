# Project Instructions

> Gender ideation survey

## Guidelines

This is a dissertation data-exploration project on **gender ideology, individual
practice, and intergenerational reproduction** in Chinese survey data. The research
questions are in `docs/SPEC.md` (sections 5.1–5.7).

**Workflow conventions:**
- **Commit and push after every completed task** (to `origin/main`).
- **TDD:** write failing tests in `tests/` (pytest) for analytic helpers before
  implementing, then run on real data. Start exploration from CFPS.
- **Raw data lives in `surveys/` and is gitignored** — never commit `.dta`/raw data.
- **All exploration output goes in `outputs/survey_exploration/`** following the
  structure in `docs/SPEC.md` §9 (inventory tables, `analysis_runs/<id>/` with
  `00_question.md` → `05_interpretation_note.md`, shared scripts in `scripts/`).
- Canonical gender-ideation recoding is `outputs/survey_exploration/scripts/ideation_lib.py`;
  it reproduces `surveys/processed/` exactly (index: [0,1], 1 = most traditional).
- Read real value labels before assigning variable direction; convert missing codes to
  NaN; never treat code values (province/occupation) as continuous (see SPEC §7, §12).

## Shared Memory

**Always write new instructions, rules, and memory to `AGENTS.md` only.**

Never modify `CLAUDE.md` or `GEMINI.md` directly - they only import `AGENTS.md`.
This ensures Claude Code, Codex CLI, and Gemini CLI share the same context consistently.

## Project Structure

- `.claude/agents/` - Custom subagents for specialized tasks
- `.claude/skills/` - Claude Code skills (slash commands)
- `.claude/rules/` - Modular rules auto-loaded into context
- `.codex/skills/` - Codex CLI skills
- `.codex/prompts/` - Codex CLI custom slash commands
- `.gemini/skills/` - Gemini CLI skills
- `.gemini/commands/` - Gemini CLI custom slash commands (TOML)
- `.mcp.json` - MCP server configuration
