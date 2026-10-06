import type { Dataset, ColumnSchema, DatasetProfile } from '../lib/datasetParser';

export interface VerificationDetails {
  operation: string;
  group_column?: string;
  metric_column?: string;
  aggregation?: string;
  sort?: string;
  limit?: number;
}

export interface VisualizationSpec {
  type: 'bar' | 'line' | 'scatter' | 'table' | 'kpi' | 'pie' | 'histogram' | 'none' | 'area' | 'donut' | 'box';
  title?: string;
  x?: string;
  y?: string;
  data?: any[];
}

export interface ClarificationOption {
  label: string;
  value: string;
}

export interface AnalysisResponse {
  success: boolean;
  answer: string;
  result?: any;
  visualization?: VisualizationSpec;
  verification?: VerificationDetails;
  error?: string;
  clarificationRequired?: boolean;
  clarificationPrompt?: string;
  clarificationOptions?: ClarificationOption[];
  audioUrl?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

export async function uploadDataset(file: File): Promise<Dataset> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/datasets/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('Failed to upload dataset');
  const data = await res.json();
  
  // Fetch full details
  const schema = await getSchema(data.dataset_id);
  const profile = await getProfile(data.dataset_id);
  
  return {
    id: data.dataset_id,
    name: data.filename,
    fileType: data.file_type,
    rows: data.rows,
    columns: data.columns,
    schema,
    profile,
    preview: []
  };
}

export async function getDataset(datasetId: string): Promise<Dataset> {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}`);
  if (!res.ok) throw new Error('Failed to get dataset');
  const data = await res.json();
  return {
    id: data.dataset_id,
    name: data.filename,
    fileType: data.file_type,
    rows: data.rows,
    columns: data.columns,
    schema: [],
    profile: { rowCount: data.rows, columnCount: data.columns, missingPercentage: 0, duplicatePercentage: 0 },
    preview: []
  };
}

export async function getSchema(datasetId: string): Promise<ColumnSchema[]> {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/schema`);
  if (!res.ok) throw new Error('Failed to get schema');
  const data = await res.json();
  
  return data.column_details.map((col: any) => ({
    name: col.name,
    dataType: col.inferred_type || col.pandas_dtype,
    role: col.semantic_role === 'categorical' ? 'Category' : 
          col.semantic_role === 'numeric_metric' ? 'Numeric' : 
          col.semantic_role === 'numeric_measure' ? 'Numeric' : 
          col.semantic_role === 'datetime' ? 'Date' : 'Text',
    missingCount: col.missing_count
  }));
}

export async function getProfile(datasetId: string): Promise<DatasetProfile> {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/profile`);
  if (!res.ok) throw new Error('Failed to get profile');
  const data = await res.json();
  
  // Calculate total missing percentage across all columns
  let totalMissing = 0;
  data.column_profiles.forEach((p: any) => {
    totalMissing += p.missing_count || 0;
  });
  const missingPercentage = data.rows > 0 ? (totalMissing / (data.rows * data.columns)) : 0;
  
  return {
    rowCount: data.rows,
    columnCount: data.columns,
    missingPercentage: missingPercentage,
    duplicatePercentage: 0, // backend doesn't provide this at dataset level easily
    columnProfiles: data.column_profiles
  };
}

export async function askQuestion(datasetId: string, question: string): Promise<AnalysisResponse> {
  try {
    const res = await fetch(`${API_BASE}/datasets/${datasetId}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    
    const data = await res.json();
    if (!res.ok) {
        return {
          success: false,
          answer: data.error?.message || "DATLY couldn't process your request.",
          error: data.error?.code || "INTERNAL_ERROR"
        };
    }
    
    // Map backend response to frontend format
    // Backend returns visualization with type, x, y. The data is in result.data or result._external_result.rows
    let visData: any[] = [];
    if (data.result && data.result.data) {
        visData = data.result.data;
    } else if (data.result && data.result._external_result && data.result._external_result.rows) {
        visData = data.result._external_result.rows;
    } else if (data.result && 'value' in data.result) {
        visData = [{ value: data.result.value }];
    }
    
    return {
      success: true,
      answer: data.answer,
      result: data.result,
      visualization: data.visualization ? {
        ...data.visualization,
        data: visData
      } : undefined,
      verification: data.analysis_plan
    };
  } catch {
    return {
      success: false,
      answer: "DATLY couldn't connect to the analytics engine.",
      error: "Backend unavailable"
    };
  }
}

export interface VoiceAnalysisResponse extends AnalysisResponse {
  transcript: string;
  audioUrl?: string;
}

export async function analyzeVoice(datasetId: string, audioBlob: Blob): Promise<VoiceAnalysisResponse> {
  try {
    const formData = new FormData();
    formData.append('dataset_id', datasetId);
    formData.append('file', audioBlob, 'audio.webm');

    const res = await fetch(`${API_BASE}/voice/analyze`, {
      method: 'POST',
      body: formData
    });
    
    const data = await res.json();
    if (!res.ok) {
        return {
          success: false,
          transcript: '',
          answer: data.error?.message || "DATLY couldn't process your request.",
          error: data.error?.code || "INTERNAL_ERROR"
        };
    }
    
    let visData: any[] = [];
    if (data.result && data.result.data) {
        visData = data.result.data;
    } else if (data.result && data.result._external_result && data.result._external_result.rows) {
        visData = data.result._external_result.rows;
    } else if (data.result && 'value' in data.result) {
        visData = [{ value: data.result.value }];
    }
    
    return {
      success: true,
      transcript: data.transcript,
      answer: data.answer,
      result: data.result,
      visualization: data.visualization ? {
        ...data.visualization,
        data: visData
      } : undefined,
      verification: data.analysis_plan,
      audioUrl: data.audio?.audio_url
    };
  } catch {
    return {
      success: false,
      transcript: '',
      answer: "DATLY couldn't connect to the voice analytics engine.",
      error: "Backend unavailable"
    };
  }
}
