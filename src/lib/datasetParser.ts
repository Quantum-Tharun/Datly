export type SemanticRole = 'ID' | 'Text' | 'Category' | 'Numeric' | 'Date';

export interface ColumnSchema {
  name: string;
  dataType: string;
  role: SemanticRole;
  missingCount: number;
}

export interface DatasetProfile {
  rowCount: number;
  columnCount: number;
  missingPercentage: number;
  duplicatePercentage: number;
  columnProfiles?: any[];
}

export interface Dataset {
  id: string;
  name: string;
  fileType: string;
  rows: number;
  columns: number;
  schema: ColumnSchema[];
  profile: DatasetProfile;
  preview: Record<string, string | number>[];
}

