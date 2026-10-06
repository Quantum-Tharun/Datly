import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, ScatterChart, Scatter, CartesianGrid, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import type { VisualizationSpec } from '../../services/api';

const COLORS = ['#a78bfa', '#f97316', '#3b82f6', '#10b981', '#f43f5e', '#f59e0b', '#8b5cf6', '#ec4899'];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#1a1a1a] border border-white/10 p-3 rounded-lg shadow-xl">
        {label && <p className="text-white/60 text-xs mb-1 uppercase tracking-wider">{label}</p>}
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-white text-sm font-mono">
            <span className="text-[#a78bfa] mr-2">{entry.name}:</span>
            {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export function ChartRenderer({ spec }: { spec: VisualizationSpec }) {
  if (!spec.data || spec.data.length === 0) return null;

  switch (spec.type) {
    case 'bar':
      return (
        <div className="h-64 w-full mt-4 bg-white/[0.02] border border-white/5 rounded-xl p-4">
          <h4 className="text-white/60 text-xs uppercase tracking-wider mb-4 font-semibold">{spec.title}</h4>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={spec.data} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
              <XAxis 
                dataKey={spec.x} 
                stroke="#ffffff40" 
                fontSize={11} 
                tickLine={false} 
                axisLine={false}
                tick={{ fill: '#ffffff60' }}
              />
              <YAxis 
                stroke="#ffffff40" 
                fontSize={11} 
                tickLine={false} 
                axisLine={false}
                tick={{ fill: '#ffffff60' }}
                tickFormatter={(value) => value >= 1000000 ? `${(value/1000000).toFixed(1)}M` : value >= 1000 ? `${(value/1000).toFixed(1)}K` : value}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: '#ffffff05' }} />
              <Bar dataKey={spec.y || ''} fill="#a78bfa" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      );

    case 'histogram': {
      // Map data to create a label for the X axis and ensure we use 'count' for Y axis
      const histData = spec.data.map(d => ({
        ...d,
        rangeLabel: `${typeof d.bin_start === 'number' ? d.bin_start.toFixed(1) : d.bin_start} - ${typeof d.bin_end === 'number' ? d.bin_end.toFixed(1) : d.bin_end}`,
        count: d.count
      }));
      
      return (
        <div className="h-64 w-full mt-4 bg-white/[0.02] border border-white/5 rounded-xl p-4">
          <h4 className="text-white/60 text-xs uppercase tracking-wider mb-4 font-semibold">{spec.title}</h4>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={histData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }} barCategoryGap={1}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
              <XAxis 
                dataKey="rangeLabel" 
                stroke="#ffffff40" 
                fontSize={10} 
                tickLine={false} 
                axisLine={false}
                tick={{ fill: '#ffffff60' }}
              />
              <YAxis 
                stroke="#ffffff40" 
                fontSize={11} 
                tickLine={false} 
                axisLine={false}
                tick={{ fill: '#ffffff60' }}
                tickFormatter={(value) => value >= 1000000 ? `${(value/1000000).toFixed(1)}M` : value >= 1000 ? `${(value/1000).toFixed(1)}K` : value}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: '#ffffff05' }} />
              <Bar dataKey="count" fill="#a78bfa" stroke="#ffffff20" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      );
    }

    case 'line':
      return (
        <div className="h-64 w-full mt-4 bg-white/[0.02] border border-white/5 rounded-xl p-4">
          <h4 className="text-white/60 text-xs uppercase tracking-wider mb-4 font-semibold">{spec.title}</h4>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={spec.data} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
              <XAxis 
                dataKey={spec.x} 
                stroke="#ffffff40" 
                fontSize={11} 
                tickLine={false} 
                axisLine={false}
                tick={{ fill: '#ffffff60' }}
              />
              <YAxis 
                stroke="#ffffff40" 
                fontSize={11} 
                tickLine={false} 
                axisLine={false}
                tick={{ fill: '#ffffff60' }}
                tickFormatter={(value) => value >= 1000000 ? `${(value/1000000).toFixed(1)}M` : value >= 1000 ? `${(value/1000).toFixed(1)}K` : value}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey={spec.y || ''} stroke="#a78bfa" strokeWidth={2} dot={{ fill: '#a78bfa', strokeWidth: 0, r: 4 }} activeDot={{ r: 6, fill: '#fff' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      );

    case 'area':
      return (
        <div className="h-64 w-full mt-4 bg-white/[0.02] border border-white/5 rounded-xl p-4">
          <h4 className="text-white/60 text-xs uppercase tracking-wider mb-4 font-semibold">{spec.title}</h4>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={spec.data} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
              <XAxis 
                dataKey={spec.x} 
                stroke="#ffffff40" 
                fontSize={11} 
                tickLine={false} 
                axisLine={false}
                tick={{ fill: '#ffffff60' }}
              />
              <YAxis 
                stroke="#ffffff40" 
                fontSize={11} 
                tickLine={false} 
                axisLine={false}
                tick={{ fill: '#ffffff60' }}
                tickFormatter={(value) => value >= 1000000 ? `${(value/1000000).toFixed(1)}M` : value >= 1000 ? `${(value/1000).toFixed(1)}K` : value}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey={spec.y || ''} stroke="#a78bfa" fill="#a78bfa" fillOpacity={0.3} strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      );

    case 'pie':
    case 'donut':
      return (
        <div className="h-64 w-full mt-4 bg-white/[0.02] border border-white/5 rounded-xl p-4 flex flex-col items-center">
          <h4 className="text-white/60 text-xs uppercase tracking-wider mb-2 font-semibold w-full text-left">{spec.title}</h4>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={spec.data}
                dataKey={spec.y || 'value'}
                nameKey={spec.x || 'name'}
                cx="50%"
                cy="50%"
                innerRadius={spec.type === 'donut' ? 60 : 0}
                outerRadius={80}
                fill="#8884d8"
                label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {spec.data.map((_entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      );

    case 'kpi': {
      const data = spec.data as any[];
      const kpiValue = data[0] && 'value' in data[0] 
        ? data[0].value 
        : (data[0] ? Object.values(data[0])[0] : null);
        
      return (
        <div className="mt-4 bg-white/[0.02] border border-white/5 rounded-xl p-6 flex flex-col items-center justify-center text-center">
          <h4 className="text-white/60 text-xs uppercase tracking-wider mb-2 font-semibold">{spec.title}</h4>
          <p className="text-3xl font-light text-white tracking-tight">
            {typeof kpiValue === 'number' 
              ? kpiValue.toLocaleString() 
              : kpiValue}
          </p>
        </div>
      );
    }
      
    case 'scatter':
      return (
        <div className="h-64 w-full mt-4 bg-white/[0.02] border border-white/5 rounded-xl p-4">
          <h4 className="text-white/60 text-xs uppercase tracking-wider mb-4 font-semibold">{spec.title}</h4>
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
              <XAxis type="number" dataKey={spec.x} name={spec.x} stroke="#ffffff40" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis type="number" dataKey={spec.y} name={spec.y} stroke="#ffffff40" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
              <Scatter name={spec.title} data={spec.data} fill="#a78bfa" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      );
      
    case 'box': {
      // Find global min and max to scale the SVG
      let globalMin = Infinity;
      let globalMax = -Infinity;
      
      spec.data.forEach((r: any) => {
        if (typeof r.min === 'number' && r.min < globalMin) globalMin = r.min;
        if (typeof r.max === 'number' && r.max > globalMax) globalMax = r.max;
        if (r.outliers) {
          r.outliers.forEach((o: number) => {
            if (o < globalMin) globalMin = o;
            if (o > globalMax) globalMax = o;
          });
        }
      });
      
      if (globalMin === Infinity) globalMin = 0;
      if (globalMax === -Infinity) globalMax = 100;
      const range = globalMax - globalMin || 1;
      const getPct = (val: number) => `${((val - globalMin) / range) * 100}%`;

      return (
        <div className="max-h-[28rem] w-full mt-4 bg-white/[0.02] border border-white/5 rounded-xl p-4 overflow-y-auto">
          <h4 className="text-white/60 text-xs uppercase tracking-wider mb-4 font-semibold">{spec.title}</h4>
          <div className="flex flex-col gap-6">
            {spec.data.map((row: any, i: number) => (
              <div key={i} className="flex flex-col bg-[#111] p-4 rounded-xl border border-white/5">
                {spec.x && row[spec.x] && (
                  <span className="text-white/80 text-sm font-semibold mb-3">{row[spec.x]}</span>
                )}
                
                {/* Visual SVG Box Plot */}
                <div className="relative w-full h-12 mt-2 mb-6 px-1">
                   <svg width="100%" height="100%" style={{ overflow: 'visible' }}>
                      {/* Whiskers (Line from min to max) */}
                      <line x1={getPct(row.min)} y1="50%" x2={getPct(row.max)} y2="50%" stroke="#ffffff40" strokeWidth="2" strokeDasharray="4 4" />
                      
                      {/* Min & Max caps */}
                      <line x1={getPct(row.min)} y1="20%" x2={getPct(row.min)} y2="80%" stroke="#ffffff80" strokeWidth="2" />
                      <line x1={getPct(row.max)} y1="20%" x2={getPct(row.max)} y2="80%" stroke="#ffffff80" strokeWidth="2" />
                      
                      {/* Box (Q1 to Q3) */}
                      <rect 
                         x={getPct(row.q1)} 
                         y="15%" 
                         width={`${((row.q3 - row.q1) / range) * 100}%`} 
                         height="70%" 
                         fill="#a78bfa" 
                         fillOpacity="0.3"
                         stroke="#a78bfa"
                         strokeWidth="2"
                         rx="4"
                      />
                      
                      {/* Median Line */}
                      <line x1={getPct(row.median)} y1="15%" x2={getPct(row.median)} y2="85%" stroke="#10b981" strokeWidth="3" />
                      
                      {/* Outliers */}
                      {row.outliers?.map((o: number, idx: number) => (
                         <circle key={idx} cx={getPct(o)} cy="50%" r="3" fill="#f43f5e" />
                      ))}
                   </svg>
                </div>

                <div className="grid grid-cols-5 gap-2 text-center mb-1">
                  <div className="text-white/40 text-[10px] uppercase">Min</div>
                  <div className="text-white/40 text-[10px] uppercase">Q1</div>
                  <div className="text-white/40 text-[10px] uppercase">Median</div>
                  <div className="text-white/40 text-[10px] uppercase">Q3</div>
                  <div className="text-white/40 text-[10px] uppercase">Max</div>
                </div>
                <div className="grid grid-cols-5 gap-2 text-center">
                  <div className="text-white font-mono text-xs">{typeof row.min === 'number' ? row.min.toLocaleString(undefined, {maximumFractionDigits: 1}) : '-'}</div>
                  <div className="text-white font-mono text-xs">{typeof row.q1 === 'number' ? row.q1.toLocaleString(undefined, {maximumFractionDigits: 1}) : '-'}</div>
                  <div className="text-[#10b981] font-mono text-xs font-bold">{typeof row.median === 'number' ? row.median.toLocaleString(undefined, {maximumFractionDigits: 1}) : '-'}</div>
                  <div className="text-white font-mono text-xs">{typeof row.q3 === 'number' ? row.q3.toLocaleString(undefined, {maximumFractionDigits: 1}) : '-'}</div>
                  <div className="text-white font-mono text-xs">{typeof row.max === 'number' ? row.max.toLocaleString(undefined, {maximumFractionDigits: 1}) : '-'}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }
      
    case 'table':
      const columns = spec.data.length > 0 ? Object.keys(spec.data[0]) : [];
      return (
        <div className="w-full mt-4 bg-white/[0.02] border border-white/5 rounded-xl overflow-hidden">
          {spec.title && (
            <h4 className="text-white/60 text-xs uppercase tracking-wider p-4 border-b border-white/5 font-semibold">
              {spec.title}
            </h4>
          )}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-white/[0.02] border-b border-white/5">
                <tr>
                  {columns.map(col => (
                    <th key={col} className="px-4 py-2 font-medium text-white/60 capitalize">{col.replace(/_/g, ' ')}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {spec.data.map((row, i) => (
                  <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                    {columns.map(col => (
                      <td key={col} className="px-4 py-2 text-white/80 font-mono text-xs">
                        {typeof row[col] === 'number' ? row[col].toLocaleString() : row[col]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );

    default:
      return null;
  }
}
