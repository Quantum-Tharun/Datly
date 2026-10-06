import type { VerificationDetails as TVerificationDetails } from '../../services/api';
import { ShieldCheck, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

export function VerificationDetails({ details }: { details: TVerificationDetails }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="flex flex-col gap-2 mt-2 pt-4 border-t border-white/10">
      <button 
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full group"
      >
        <div className="flex items-center gap-2">
          <ShieldCheck size={14} className="text-[#a78bfa]" />
          <span className="text-xs text-[#a78bfa]/80 uppercase tracking-wider font-semibold">Verified Analysis</span>
        </div>
        <div className="text-white/40 group-hover:text-white/70 transition-colors">
          {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </div>
      </button>

      {open && (
        <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
          <div className="bg-white/5 border border-white/10 rounded-lg px-3 py-2">
            <span className="text-white/40 block mb-0.5">Operation</span>
            <span className="text-white/80 font-mono capitalize">{details.operation.replace('_', ' ')}</span>
          </div>
          {details.group_column && (
            <div className="bg-white/5 border border-white/10 rounded-lg px-3 py-2">
              <span className="text-white/40 block mb-0.5">Grouped By</span>
              <span className="text-white/80 font-mono capitalize">{details.group_column}</span>
            </div>
          )}
          {details.metric_column && (
            <div className="bg-white/5 border border-white/10 rounded-lg px-3 py-2">
              <span className="text-white/40 block mb-0.5">Metric</span>
              <span className="text-white/80 font-mono capitalize">{details.metric_column}</span>
            </div>
          )}
          {details.aggregation && (
            <div className="bg-white/5 border border-white/10 rounded-lg px-3 py-2">
              <span className="text-white/40 block mb-0.5">Aggregation</span>
              <span className="text-white/80 font-mono capitalize">{details.aggregation}</span>
            </div>
          )}
          {details.sort && (
            <div className="bg-white/5 border border-white/10 rounded-lg px-3 py-2">
              <span className="text-white/40 block mb-0.5">Sort</span>
              <span className="text-white/80 font-mono capitalize">{details.sort === 'desc' ? 'Highest first' : 'Lowest first'}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
