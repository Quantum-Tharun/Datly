# DATLY API Contract

This document serves as the official API contract for the DATLY frontend integration.

## 1. Base URL
All API requests should be prefixed with the following base URL:
`http://localhost:8000/api/v1`

## 2. Authentication Status
Currently, the DATLY API does **not** require authentication. All endpoints are publicly accessible for development.

## 3. Endpoint List

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Verify that the backend is running. |
| POST | `/datasets/upload` | Upload a new dataset (CSV, XLSX, JSON). |
| GET | `/datasets/{dataset_id}` | Retrieve metadata for an uploaded dataset. |
| GET | `/datasets/{dataset_id}/schema` | Retrieve inferred schema information. |
| GET | `/datasets/{dataset_id}/profile` | Retrieve dataset statistical profile. |
| POST | `/datasets/{dataset_id}/analyze` | Submit a natural language question for analysis. |

---

## 4. Frontend Workflow

The intended frontend workflow is as follows:

1. **Upload**: `POST /datasets/upload` (Receive `dataset_id`)
2. **Get Metadata**: `GET /datasets/{dataset_id}`
3. **Get Schema**: `GET /datasets/{dataset_id}/schema`
4. **Get Profile**: `GET /datasets/{dataset_id}/profile`
5. **User enters a question**
6. **Submit Analysis**: `POST /datasets/{dataset_id}/analyze`
7. **Render Result**: Render `answer` (text), `result` (table/data), and `visualization` (chart).

---

## 5. Request & Response Contracts

### GET `/health`
**Response:**
```json
{
    "status": "ok"
}
```

### POST `/datasets/upload`
**Content-Type:** `multipart/form-data`
**Request:** `file` (Form field containing the dataset file. Supported: `.csv`, `.xlsx`, `.json`. Max Size: 50MB)
**Response:**
```json
{
    "dataset_id": "ds_a83f21c9",
    "filename": "sales.csv",
    "file_type": "csv",
    "rows": 1000,
    "columns": 8,
    "created_at": "2026-10-05T12:30:00Z"
}
```

### GET `/datasets/{dataset_id}`
**Response:**
```json
{
    "dataset_id": "ds_a83f21c9",
    "filename": "sales.csv",
    "file_type": "csv",
    "rows": 1000,
    "columns": 8,
    "created_at": "2026-10-05T12:30:00Z"
}
```

### GET `/datasets/{dataset_id}/schema`
**Response:**
```json
{
    "dataset_id": "ds_a83f21c9",
    "columns": [
        {
            "name": "revenue",
            "pandas_dtype": "float64",
            "inferred_type": "numeric",
            "semantic_role": "metric",
            "nullable": true,
            "missing_count": 0,
            "missing_percentage": 0.0,
            "unique_count": 500,
            "unique_percentage": 50.0,
            "sample_values": [150.5, 200.0]
        }
    ]
}
```

### POST `/datasets/{dataset_id}/analyze`
**Request:**
```json
{
    "question": "Which city generated the highest revenue?"
}
```
**Response:**
```json
{
    "success": true,
    "dataset_id": "ds_123",
    "question": "Which city generated the highest revenue?",
    "answer": "Coimbatore has the highest revenue with a value of 8,250,000.",
    "result": {
        "data": [
            {
                "city": "Coimbatore",
                "revenue": 8250000
            }
        ]
    },
    "visualization": {
        "type": "bar",
        "x": "city",
        "y": "revenue",
        "title": "Revenue by City"
    },
    "analysis_plan": {
        "operation": "top_n",
        "metric_column": "revenue",
        "group_column": "city",
        "filters": null,
        "aggregation": "sum",
        "sort": "desc",
        "sort_column": null,
        "limit": 1,
        "visualization": "bar"
    }
}
```

---

## 6. Visualization Contract

The backend **does not** render chart images. It returns a strict `VisualizationSpec` object that the frontend maps to a UI charting library.

**Supported Types:**
- `bar`: For categorical comparisons or rankings.
- `line`: For temporal/trend analysis.
- `scatter`: For numeric vs. numeric comparisons.
- `table`: For tabular data without a direct chart mapping.
- `none`: For scalar values (e.g. total sums) or empty queries.

**Example Spec:**
```json
{
    "type": "bar",
    "x": "city",
    "y": "revenue",
    "title": "Revenue by City"
}
```

---

## 7. Error Format & Codes

All structured errors follow this format:
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable explanation of the error."
    }
}
```

**Known Error Codes:**
- `DATASET_NOT_FOUND`: The requested dataset ID does not exist in memory.
- `LLM_NOT_CONFIGURED`: NVIDIA API Key is missing.
- `NVIDIA_API_FAILURE`: Upstream failure from the NVIDIA NIM endpoint.
- `INVALID_ANALYSIS_PLAN`: The LLM returned an invalid or malformed schema.
- `ANALYTICS_ERROR`: The execution engine failed to parse or execute the deterministic pandas logic.
- `INTERNAL_ERROR`: General failure processing data or schemas.

## 8. HTTP Status Codes
- `200 OK`: Successful requests.
- `400 Bad Request`: Validation failures (e.g., malformed JSON plans).
- `404 Not Found`: Datasets that do not exist.
- `500 Internal Server Error`: Backend execution failures or API upstream timeouts.
