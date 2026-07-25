---
name: task-decomposer
description: >-
  Decomposes complex multi-step goals into ordered, verifiable subtasks with
  acceptance criteria and dependency graphs. Use when the user says break this
  down, decompose, create subtasks, task decomposer, plan the work, or when a
  feature spans multiple layers and needs an executable task list.
---

# Task Decomposer

Thin Job Pilot entrypoint for task breakdown. Follow the full workflow in
`planning-and-task-breakdown` (same repo skills folder).

## Instructions

1. Read and follow `.agents/skills/planning-and-task-breakdown/SKILL.md` (or `.cursor/skills/planning-and-task-breakdown/SKILL.md`).
2. Prefer vertical slices over horizontal layer builds.
3. Write outputs to `tasks/plan.md` and `tasks/todo.md` unless the user names another path.
4. Every task must have: goal, files touched, acceptance criteria, and blockers.
5. Do not implement during decomposition — plan only until the user confirms.

## Job Pilot defaults

When decomposing Job Pilot work, keep these constraints visible in the plan:

- Israeli market focus (IL jobs + remote roles open to Israeli developers)
- BYO AI keys only (no free/site-provided model)
- Memory + Dreaming feed RAG before outreach generation
- External platforms via MCP (never scrape credentials through the agent)
