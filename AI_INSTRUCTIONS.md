# AI Context Brain Instructions

## Generation Metadata
- Plan: Free
- Context Capacity Applied: 100% of selected allowance
- Source: template
- Context History Saved: no
- Validation Warnings: none

# AI Instructions for InFlux

Use the generated `.ai-context.md` as the source of truth before editing this repository.

## Project Summary
- Purpose: Application organized around Authentication, Projects, Email / Notifications, Dashboard Client.
- Architecture: Standard
- Frameworks: Python
- Database: fresh scan required
- Authentication: fresh scan required

## Required AI Workflow and Project Rules
- Read `.ai-context.md` before editing and use it as the source of truth for architecture and project memory.
- Do not hardcode secrets, tokens, connection strings, provider keys, webhook secrets, or email credentials.
- Reuse existing services, controllers, hooks, context providers, and extension command patterns before adding new abstractions.
- Keep server-side authorization, tenant/project scoping, and plan enforcement in backend code; UI checks are only an additional guard.
- When changing API contracts, update the dashboard, extension client, tests, and documentation together.
- Prefer incremental, focused changes and verify with the available build/test commands.

## Module Boundaries
- Authentication: User registration, login, JWT/refresh token management, email verification, and password reset. Key files: `htmlcov/z_76373084f9525252_authority_py.html`, `.venv-2/lib/python3.14/site-packages/pip-25.1.1.dist-info/licenses/AUTHORS.txt`, `.venv-2/lib64/python3.14/site-packages/pip-25.1.1.dist-info/licenses/AUTHORS.txt`, `.venv-3/lib64/python3.14/site-packages/pygments-2.20.0.dist-info/licenses/AUTHORS`.
- Projects: Project CRUD, scan uploads, context generation triggers, and context history management. Key files: `pyproject.toml`, `PROJECT_STATE.md`, `docs/PROJECT_BLUEPRINT.md`, `.venv-2/lib/python3.14/site-packages/pip/_vendor/pyproject_hooks/__init__.py`.
- Email / Notifications: Transactional email via Resend API for verification, password reset, and admin test emails. Key files: `.venv-3/lib64/python3.14/site-packages/pygments/lexers/email.py`, `.venv-3/lib/python3.14/site-packages/pygments/lexers/email.py`, `.venv-4/lib/python3.14/site-packages/pygments/lexers/email.py`, `.venv-4/lib64/python3.14/site-packages/pygments/lexers/email.py`.
- Dashboard Client: React SPA displaying project memories, context history, settings, team management, and billing. Key files: `htmlcov/z_d2dca0d2db53f1cc_dashboard_py.html`, `tests/audit/test_repository_health_dashboard.py`, `scripts/audit/repository_health_dashboard.py`, `dashboard/app.py`.
- Entitlements & Licensing: Plan capabilities, quotas and server-side feature enforcement. Key files: `htmlcov/coverage_html_cb_dd2e7eb5.js`.

## Required AI Workflow
- Read .ai-context.md before implementing changes.
- Preserve architecture rules, naming rules, import rules, and folder boundaries.
- Prefer existing services and modules over new abstractions.
- Do not hardcode secrets, tokens, connection strings, or provider keys.
- Keep changes scoped and verify builds/tests when possible.
