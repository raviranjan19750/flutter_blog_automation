# Flutter Blog Automation

Automated generation and selection of blog topics using Python and GitHub Actions.

## Setup

1. **Create Virtual Environment** (already done if `.venv` exists):
   ```bash
   python3 -m venv .venv
   ```

2. **Activate Environment**:
   - macOS/Linux: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\activate`

3. **Install Dependencies**:
   ```bash
   pip install -r scripts/requirements.txt
   ```

## Workflow
- Topics are defined in `config/topics.json`.
- Scripts in `scripts/` handle topic selection and draft generation.
- GitHub Actions automate the process via `.github/workflows/generate-draft.yml`.
