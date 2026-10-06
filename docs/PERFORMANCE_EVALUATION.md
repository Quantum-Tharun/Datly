# Datly Performance Evaluation

## Overview
This document contains the performance evaluation of the Datly Analytics Engine under deterministic workloads.

## Methodology
- **Hardware**: Developer Local Machine (Standard CI Environment equivalence)
- **Software**: Python 3.11, Pandas Engine
- **Dataset Size**: 100,000 rows x 3 columns (Categorical, Numeric, Datetime)
- **Queries Evaluated**: Random mix of `sum`, `average`, `group_by`, and `percentage` (including visualization schema building).
- **Metric Definitions**:
  - **Query Accuracy**: 100% deterministic (no LLM hallucination in analytics execution layer).
  - **Sequential Test**: 100 queries run serially.
  - **Concurrent Test**: 200 queries run with a concurrency level of 10 workers (simulating multiple users).

## Real Benchmark Results
Based on actual measurements logged in `benchmark_results.json`:

| Metric | Result |
|---|---|
| **Query Accuracy** | 100% |
| **Dataset Rows** | 100,000 |
| **p50 Latency** | 0.0074 seconds |
| **p95 Latency** | 0.0140 seconds |
| **p99 Latency** | 0.0183 seconds |
| **Throughput** | 216.0 queries/second |
| **Total Concurrent Time (200 ops)**| 0.9259 seconds |

## Limitations
- In-memory execution using Pandas means the server's RAM determines the maximum ingestible dataset size limit (currently suitable up to ~5-10 million rows depending on host).
- ThreadPool execution is partially bound by Python's GIL. True scaling out requires multiprocess execution (e.g., Uvicorn workers) or external OLAP integrations for billions of rows.
