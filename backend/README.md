# DATLY Backend

Backend for DATLY — Schema-Agnostic Natural Language Data Analyst.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in the values.
5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```
