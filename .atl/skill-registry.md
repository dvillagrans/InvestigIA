# Skill Registry — InvestigIA

Index of available skills for this project. Each skill is matched by trigger/context and loaded by exact path.

| Skill | Trigger / Description | Scope | Path |
|-------|----------------------|-------|------|
| redaccion-academica | Redactar, reescribir, pulir, mejorar, humanizar texto académico. "Suena a IA", "hazlo más humano", bullet points a prosa. | user | `~/.config/opencode/skills/redaccion-academica/SKILL.md` |
| cognitive-doc-design | Writing guides, READMEs, RFCs, onboarding, architecture, review-facing docs. | user | `~/.config/opencode/skills/cognitive-doc-design/SKILL.md` |
| comment-writer | PR feedback, issue replies, reviews, Slack messages, GitHub comments. | user | `~/.config/opencode/skills/comment-writer/SKILL.md` |
| skill-creator | New skills, agent instructions, documenting AI usage patterns. | user | `~/.config/opencode/skills/skill-creator/SKILL.md` |
| skill-improver | Improve skills, audit skills, refactor skills, skill quality. | user | `~/.config/opencode/skills/skill-improver/SKILL.md` |
| skill-registry | Update skills, skill registry, after skill changes. | user | `~/.config/opencode/skills/skill-registry/SKILL.md` |
| branch-pr | Creating, opening, or preparing PRs for review. | user | `~/.config/opencode/skills/branch-pr/SKILL.md` |
| chained-pr | PRs over 400 lines, stacked PRs, review slices. | user | `~/.config/opencode/skills/chained-pr/SKILL.md` |
| issue-creation | Creating GitHub issues, bug reports, or feature requests. | user | `~/.config/opencode/skills/issue-creation/SKILL.md` |
| work-unit-commits | Implementation, commit splitting, chained PRs, tests with code. | user | `~/.config/opencode/skills/work-unit-commits/SKILL.md` |
| judgment-day | Judgment day, dual review, adversarial review. | user | `~/.config/opencode/skills/judgment-day/SKILL.md` |
| go-testing | Go tests, go test coverage, Bubbletea teatest, golden files. | user | `~/.config/opencode/skills/go-testing/SKILL.md` |
| sdd-explore | Explore SDD ideas before committing to a change. | user | `~/.config/opencode/skills/sdd-explore/SKILL.md` |
| sdd-propose | Create change proposals from explorations. | user | `~/.config/opencode/skills/sdd-propose/SKILL.md` |
| sdd-spec | Write detailed specifications from proposals. | user | `~/.config/opencode/skills/sdd-spec/SKILL.md` |
| sdd-design | Create technical design from proposals. | user | `~/.config/opencode/skills/sdd-design/SKILL.md` |
| sdd-tasks | Break down specs and designs into implementation tasks. | user | `~/.config/opencode/skills/sdd-tasks/SKILL.md` |
| sdd-apply | Implement code changes from task definitions. | user | `~/.config/opencode/skills/sdd-apply/SKILL.md` |
| sdd-verify | Validate implementation against specs. | user | `~/.config/opencode/skills/sdd-verify/SKILL.md` |
| sdd-archive | Archive completed change artifacts. | user | `~/.config/opencode/skills/sdd-archive/SKILL.md` |
| sdd-init | Initialize SDD context, testing capabilities, registry. | user | `~/.config/opencode/skills/sdd-init/SKILL.md` |
| sdd-onboard | Guide user through a complete SDD cycle. | user | `~/.config/opencode/skills/sdd-onboard/SKILL.md` |

---

## Usage

When delegating work, match skills by file context (extensions, paths) and task context (review, PR creation, testing, etc.). Copy matching `SKILL.md` paths into the sub-agent prompt as `## Skills to load before work`.

## Registry Contract

- Source of truth: each `SKILL.md` file.
- This index is for discovery only.
- Skip `sdd-*`, `_shared`, and `skill-registry` in delegation matching unless explicitly needed.
- Project-level skills override user-level skills when names conflict.
