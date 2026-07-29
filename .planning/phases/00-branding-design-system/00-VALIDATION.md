---
phase: 0
slug: branding-design-system
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-29
---

# Phase 0 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Node.js native test runner (`node:test`) |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `node --test brand/tests/*.test.js` |
| **Full suite command** | `node --test brand/tests/*.test.js` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `node --test brand/tests/*.test.js`
- **After every plan wave:** Run `node --test brand/tests/*.test.js`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 00-01-01 | 01 | 1 | BRAND-01 | — | N/A | unit | `node --test brand/tests/assets.test.js` | ❌ W0 | ⬜ pending |
| 00-02-01 | 02 | 1 | BRAND-02 | — | N/A | unit | `node --test brand/tests/tokens.test.js` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `brand/tests/assets.test.js` — validates canonical PNG existence (BRAND-01)
- [ ] `brand/tests/tokens.test.js` — validates CSS token custom properties presence and syntax (BRAND-02)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual mascot quality / no AI-slop | BRAND-01 | Subjective visual review | Open `brand/assets/` in compare gallery; spot-check against `brand-mascot-canonical.png` |
| German voice tone | BRAND-01 | Linguistic judgment | Read `brand/VOICE.md` samples aloud; confirm dry/clever, no baby talk |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
