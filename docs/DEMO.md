# DATLY Demonstration

## Assets
The `sample_data/` directory contains standard samples for evaluating Datly:
- `company_metrics.csv`
- `company_metrics.xlsx`
- `company_metrics.json`

## Setup
1. Clone repository
2. Run backend: `cd backend && uvicorn app.main:app --reload`
3. Run frontend: `cd frontend && npm run dev`

## Demonstration Walkthrough
1. Upload `sample_data/company_metrics.csv` through the chat composer attachment button.
2. Type or speak the following questions to see natural language analytics:

- "What is the total revenue?"
- "Which region has the highest headcount?"
- "Show me average headcount by department."
- "What percentage of revenue comes from Europe?"

3. Evaluate the corresponding chart visualization output and accuracy of natural language explanation.
