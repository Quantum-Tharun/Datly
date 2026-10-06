import type { Dataset } from '../../lib/datasetParser';
import { DatasetSummary } from './DatasetSummary';
import { SchemaTable } from './SchemaTable';
import { DataQuality } from './DataQuality';
import { DatasetPreviewTable } from './DatasetPreviewTable';


export function DatasetUnderstanding({ dataset }: { dataset: Dataset }) {
  // Find a primary numeric column for default insights
  let primaryNumericStats = null;
  let primaryNumericName = '';
  
  if (dataset.profile?.columnProfiles) {
    for (const col of dataset.profile.columnProfiles) {
      if (col.numeric_stats) {
        primaryNumericStats = col.numeric_stats;
        primaryNumericName = col.name;
        // Prefer a column with 'revenue', 'sales', or 'profit' in the name if possible
        if (col.name.toLowerCase().match(/revenue|sales|profit|total|amount/)) {
          break;
        }
      }
    }
  }

  return (
    <div className="flex flex-col gap-4 font-sans max-w-full">
      <DatasetSummary dataset={dataset} />
      
      {primaryNumericStats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-2">
          <div className="bg-[#1a1a1a] border border-white/10 rounded-xl p-4 flex flex-col items-center text-center">
            <span className="text-white/40 text-[10px] uppercase tracking-wider font-semibold mb-1">Total {primaryNumericName}</span>
            <span className="text-white text-lg font-light">
              {primaryNumericStats.sum != null ? primaryNumericStats.sum.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '-'}
            </span>
          </div>
          <div className="bg-[#1a1a1a] border border-white/10 rounded-xl p-4 flex flex-col items-center text-center">
            <span className="text-white/40 text-[10px] uppercase tracking-wider font-semibold mb-1">Average {primaryNumericName}</span>
            <span className="text-white text-lg font-light">
              {primaryNumericStats.mean != null ? primaryNumericStats.mean.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '-'}
            </span>
          </div>
          <div className="bg-[#1a1a1a] border border-white/10 rounded-xl p-4 flex flex-col items-center text-center">
            <span className="text-white/40 text-[10px] uppercase tracking-wider font-semibold mb-1">Highest {primaryNumericName}</span>
            <span className="text-[#10b981] text-lg font-light">
              {primaryNumericStats.max != null ? primaryNumericStats.max.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '-'}
            </span>
          </div>
          <div className="bg-[#1a1a1a] border border-white/10 rounded-xl p-4 flex flex-col items-center text-center">
            <span className="text-white/40 text-[10px] uppercase tracking-wider font-semibold mb-1">Lowest {primaryNumericName}</span>
            <span className="text-[#f43f5e] text-lg font-light">
              {primaryNumericStats.min != null ? primaryNumericStats.min.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '-'}
            </span>
          </div>
        </div>
      )}

      <SchemaTable schema={dataset.schema} />
      <DataQuality profile={dataset.profile} />
      <DatasetPreviewTable dataset={dataset} />
      
      <p className="text-white/60 text-sm mt-2">
        DATLY is ready to answer questions about this data.
      </p>
    </div>
  );
}
