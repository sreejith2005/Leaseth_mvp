# Frontend Updates Required

## Issue 1: Remove AI-Generated Aesthetic
Current site screams "AI-generated template." Needs human design touch.

**Problems:**
- Generic fonts and spacing
- Cookie-cutter animations/transitions
- Emoji usage for icons/imagery
- Predictable color gradients
- Standard SaaS template feel

**Goal:** Minimalist, professional design that feels intentionally crafted. Think human designer made deliberate choices, not template fill-in-the-blank. Remove all emojis. Use restraint with animations. Pick unexpected but tasteful typography. Make it feel custom.

## Issue 2: Dashboard Data Persistence Broken
**Current behavior:**
- Dashboard shows placeholder/dummy applicants
- After scoring new applicant, prediction displays correctly
- BUT new applicant doesn't appear in dashboard
- Dashboard data doesn't update with real submissions

**Expected behavior:**
- Dashboard should show only real scored applicants
- After each prediction, applicant should immediately appear in dashboard list
- No placeholders or mock data visible
- Real-time sync between scoring and dashboard view

**Root cause:** Either not persisting to backend database OR not fetching/displaying real data from API. Dashboard likely hardcoded with sample data instead of pulling from `GET /api/v1/applications` or equivalent endpoint.

Fix both. Make it production-ready.
