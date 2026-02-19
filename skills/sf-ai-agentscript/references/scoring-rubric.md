<!-- Parent: sf-ai-agentscript/SKILL.md -->

# Scoring System (100 Points)

## Categories

| Category | Points | Key Criteria |
|----------|--------|--------------|
| **Structure & Syntax** | 20 | Block ordering, indentation consistency, required fields present |
| **Deterministic Logic** | 25 | Security via `available when`, post-action checks, proper conditionals |
| **Instruction Resolution** | 20 | Correct use of `->` vs `|`, template injection, action execution |
| **FSM Architecture** | 15 | Clear topic separation, explicit transitions, state management |
| **Action Configuration** | 10 | Correct protocols, input/output mapping, error handling |
| **Deployment Readiness** | 10 | Valid `default_agent_user`, no compilation errors, metadata complete |

## Scoring Rubric Details

### Structure & Syntax (20 points)
| Points | Criteria |
|--------|----------|
| 20 | All required blocks present, consistent indentation, valid identifiers |
| 15 | Minor issues (e.g., inconsistent spacing within tolerance) |
| 10 | Missing optional blocks that would improve clarity |
| 5 | Block ordering issues or mixed indentation |
| 0 | Missing required blocks or compilation failures |

### Deterministic Logic (25 points)
| Points | Criteria |
|--------|----------|
| 25 | All security actions guarded with `available when`, post-action patterns used |
| 20 | Most guards present, minor gaps in deterministic enforcement |
| 15 | Some security logic relies on prompts instead of guards |
| 10 | Critical actions lack `available when` guards |
| 0 | Security logic entirely prompt-based (LLM can bypass) |

### Instruction Resolution (20 points)
| Points | Criteria |
|--------|----------|
| 20 | Arrow syntax for complex logic, proper template injection, correct action execution |
| 15 | Mostly correct, minor syntax issues |
| 10 | Uses pipe syntax where arrow needed, template injection errors |
| 5 | Incorrect phase ordering (data loads after LLM sees instructions) |
| 0 | Fundamental misunderstanding of resolution order |

### FSM Architecture (15 points)
| Points | Criteria |
|--------|----------|
| 15 | Clear topic boundaries, explicit transitions, appropriate escalation paths |
| 12 | Good structure with minor redundancy |
| 9 | Topics too broad or transitions unclear |
| 5 | Monolithic topic handling multiple concerns |
| 0 | No topic separation, all logic in start_agent |

### Action Configuration (10 points)
| Points | Criteria |
|--------|----------|
| 10 | Correct protocols, proper I/O mapping, descriptions present |
| 8 | Minor issues (missing descriptions) |
| 5 | Wrong protocol for use case |
| 2 | Input/output mapping errors |
| 0 | Actions don't compile |

### Deployment Readiness (10 points)
| Points | Criteria |
|--------|----------|
| 10 | Valid user, clean validation, metadata complete |
| 8 | Minor warnings |
| 5 | Validation errors that need fixing |
| 2 | Missing metadata files |
| 0 | Cannot deploy |

## Score Thresholds

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | ⭐⭐⭐⭐⭐ Excellent | Deploy with confidence |
| 80-89 | ⭐⭐⭐⭐ Very Good | Minor improvements recommended |
| 70-79 | ⭐⭐⭐ Good | Review flagged issues before deploy |
| 60-69 | ⭐⭐ Needs Work | Address issues before deploy |
| <60 | ⭐ Critical | **BLOCK** - Fix critical issues |

## Score Report Format
```
📊 AGENT SCRIPT SCORE REPORT
════════════════════════════════════════

Score: 85/100 ⭐⭐⭐⭐ Very Good
├─ Structure & Syntax:    18/20 (90%)
├─ Deterministic Logic:   22/25 (88%)
├─ Instruction Resolution: 16/20 (80%)
├─ FSM Architecture:      12/15 (80%)
├─ Action Configuration:   9/10 (90%)
└─ Deployment Readiness:   8/10 (80%)

Issues:
⚠️ [Deterministic] Missing `available when` on process_refund action
⚠️ [Resolution] Post-action check should be at TOP of instructions
✓ All Structure & Syntax checks passed
✓ All Action Configuration checks passed
```
