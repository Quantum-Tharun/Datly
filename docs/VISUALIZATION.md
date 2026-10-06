# DATLY Visualization System

The DATLY visualization system is designed to provide highly accurate and intelligent chart recommendations based on natural language queries, without requiring explicit chart type commands from the user. The backend serves as the authoritative source of truth for both the calculated data and the visualization type.

## Core Principle
- **Backend Driven**: The LLM planner understands the user's analytical intent, the deterministic Python engine calculates the results, and the visualization engine automatically selects the best presentation format.
- **Dumb Frontend**: The frontend merely receives a `VisualizationSpec` and renders the exact chart type specified, removing any ad-hoc visualization logic from the UI.

## Explicit vs Automatic Mode

The system handles visualization via two modes:

1. **Explicit Request (Priority)**
   If a user explicitly asks for a chart (e.g., *"Show revenue by region as a pie chart"*), the system will override automatic heuristics and render a pie chart, provided the query contains the requisite data structure (e.g., categorical dimension + numeric metric).

2. **Automatic Selection (Default)**
   If the user asks an ordinary query (e.g., *"What is revenue by region?"*), the backend runs a comprehensive heuristic engine to determine the best chart.

## Chart Selection Rules

When operating in Automatic Mode, the following rules dictate chart selection:

- **Categorical Comparison (BAR)**
  Used for ranking, top-N, bottom-N, and standard aggregations.
  *Example*: "Which cities generated the most revenue?" -> **Bar Chart**

- **Time Series / Trend (LINE)**
  Used when the grouping dimension represents chronological data (e.g., date, month, year) or the LLM identifies a `trend` operation.
  *Example*: "How did revenue change over time?" -> **Line Chart**

- **Part-to-Whole / Percentage (PIE / DONUT)**
  Used when analyzing share distribution or percentages (`percentage` operation), provided the number of categories is small (<= 10).
  *Example*: "What percentage of sales comes from each region?" -> **Pie Chart**
  *(Note: Falls back to Bar Chart if categories exceed 10 to maintain readability).*

- **Relationship / Comparison (SCATTER)**
  Used when analyzing the relationship between two independent numeric variables.
  *Example*: "What is the relationship between price and units sold?" -> **Scatter Plot**

- **Distribution (HISTOGRAM / BOX PLOT)**
  Used for frequency mapping (`histogram`) or spread/variability mapping (`box plot`) of numeric features.
  *Example*: "Show the distribution of profit." -> **Histogram / Box Plot**

- **Single Scalar (KPI)**
  Used when the query returns a single aggregated metric.
  *Example*: "What is the total revenue?" -> **KPI Indicator**

- **Large/Multidimensional Data (TABLE)**
  Used as a fallback when data contains many metrics without a clear primary visualization axis, or if an explicit table is requested.
  *Example*: "Show all transaction details." -> **Table**

## Responsibility Boundaries
- **NVIDIA NIM Planner**: Responsible ONLY for intent extraction, operation assignment, metric identification, filtering, and time granularity. Does NOT invent chart data.
- **Python Deterministic Engine (Pandas/NumPy)**: Responsible for ALL aggregation, grouping, percentages, and numeric operations.
- **Frontend (React)**: Responsible ONLY for mapping the `VisualizationSpec.type` to the corresponding Recharts component.

By adhering to this pipeline, DATLY avoids random chart assignments, hidden mock fallbacks, and unreadable visualizations.
