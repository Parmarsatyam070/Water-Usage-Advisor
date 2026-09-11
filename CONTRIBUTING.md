# Contributing to Smart Water Usage Advisor

Thank you for your interest in contributing to the **Smart Water Usage Advisor** project, supporting UN SDG 6 (Clean Water & Sanitation).

---

## 1. Development Principles
1. **Respect Canonical Architecture:** Adhere strictly to the numbered directory hierarchy (`1_DOCUMENTATION`, `2_RESEARCH_DATA`, etc.).
2. **Follow Database Naming:** Never invent or modify authoritative database table and column names (`users`, `meters`, `water_usage_data`, etc.).
3. **Keep Secrets Safe:** Never commit API keys, database passwords, or `.env` files.
4. **Clean Code & Testing:** Add unit and integration tests under `6_TESTING/` for every feature introduced.
5. **Phase-by-Phase Discipline:** Do not jump phases without explicit review and approval.

---

## 2. Getting Started
1. Fork and clone the repository.
2. Activate your local virtual environment:
   ```bash
   source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
   ```
3. Copy the template `.env.example` to `.env` for local testing.
4. Run testing checks before submitting pull requests.
