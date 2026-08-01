# AlphaLens AI

AlphaLens AI is a modular Streamlit prototype for institutional-style trading and investment decisions. Phase 1 establishes the application shell, navigation, source-data boundaries, and engineering foundation; quantitative models and document/workbook extraction follow in later phases.

## Features in Phase 1

- Responsive dark Streamlit interface with ten application modules.
- Centralized configuration, logging, error handling, and source registry.
- Source catalogue for the supplied strategy reports and risk-management workbooks.
- UI and domain/service layers are intentionally separated.
- Test-ready, GitHub-ready Python package layout.

## Project layout

```text
alphalens-ai/
├── .streamlit/             # Streamlit UI/runtime configuration
├── data/
│   ├── raw/                # Local source reports and workbooks (gitignored)
│   └── processed/          # Derived datasets (gitignored)
├── logs/                   # Local application logs (gitignored)
├── src/alphalens/
│   ├── core/               # Exceptions and logging
│   ├── domain/             # Source metadata and future domain models
│   ├── services/           # Non-UI application services
│   └── ui/                 # Streamlit app shell and pages
├── tests/                  # Automated tests
├── app.py                  # Streamlit entry point
├── requirements.txt
└── pyproject.toml
```

## Setup

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies and the local package: `pip install -r requirements.txt && pip install -e .`
3. Copy the supplied `.docx` and `.xlsx` files into `data/raw/` (they are intentionally not committed).
4. Run: `streamlit run app.py`

## Streamlit Community Cloud deployment

Deploy the **entire contents** of this repository, not `app.py` by itself. In
the repository root, the deployment should include both `app.py` and
`src/alphalens/`; `app.py` adds `src/` to the import path before loading the
modular application. It also provides a deployment-safe Phase 1 shell when a
Cloud repository contains only the entry point. Set the Cloud main file path
to `app.py`, then reboot the app after pushing the update.

## Supplied source material

The source catalogue expects these files in `data/raw/`:

- `DalalStreet_Elite_Strategy_Report.docx`
- `Enhanced_Final_Report.docx`
- `Full_Strategy_Report.docx`
- `Phase_1_Market_Understanding.docx` through `Phase_5_Derivatives_Strategies.docx`
- `BS-FIRST PRINCIPLE-STUDENT.xlsx`
- `VaR_Risk_Management_Tool.xlsx`

Phase 2 will convert these inputs into validated, traceable datasets and quantitative services. This repository does not commit personal or source data.

## Engineering conventions

- Add calculations in `src/alphalens/services/`, not in Streamlit page code.
- Keep page modules limited to presentation and input orchestration.
- Configure file locations with `ALPHALENS_DATA_DIR` when `data/raw/` is not appropriate.
- Run tests with `pytest`.
# AlphaLens AI
