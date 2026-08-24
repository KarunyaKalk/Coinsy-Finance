import React from 'react';

export const CalendarHeatmap = ({ items = [] }) => {
  if (!items || items.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 border border-dashed border-slate-200 rounded-lg text-slate-400 text-xs">
        No daily spend heatmap data available
      </div>
    );
  }

  const getIntensityClass = (level) => {
    switch (level) {
      case 1:
        return 'bg-rose-100 hover:ring-2 hover:ring-rose-300';
      case 2:
        return 'bg-rose-300 hover:ring-2 hover:ring-rose-400';
      case 3:
        return 'bg-rose-500 hover:ring-2 hover:ring-rose-600';
      case 4:
        return 'bg-rose-700 hover:ring-2 hover:ring-rose-800';
      default:
        return 'bg-slate-100 hover:bg-slate-200';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span className="font-semibold text-slate-700">Daily Spend Intensity (Last 90 Days)</span>
        <div className="flex items-center space-x-1.5">
          <span className="text-[10px]">Less</span>
          <span className="w-3 h-3 rounded bg-slate-100 border border-slate-200" title="0 spend" />
          <span className="w-3 h-3 rounded bg-rose-100" title="Low spend" />
          <span className="w-3 h-3 rounded bg-rose-300" title="Medium spend" />
          <span className="w-3 h-3 rounded bg-rose-500" title="High spend" />
          <span className="w-3 h-3 rounded bg-rose-700" title="Peak spend" />
          <span className="text-[10px]">More</span>
        </div>
      </div>

      <div className="grid grid-cols-7 sm:grid-cols-10 md:grid-cols-14 gap-1.5 max-h-56 overflow-y-auto p-1 border border-slate-100 bg-slate-50/50 rounded-lg">
        {items.map((item) => (
          <div
            key={item.date}
            className={`w-full aspect-square rounded-md transition-all cursor-pointer relative group flex items-center justify-center text-[9px] font-bold ${getIntensityClass(
              item.intensity_level
            )}`}
          >
            {/* Tooltip on Hover */}
            <div className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 hidden group-hover:block z-20 w-36 p-2 bg-slate-900 text-white rounded-md text-[11px] shadow-lg pointer-events-none space-y-0.5">
              <div className="font-semibold text-slate-300">{item.date}</div>
              <div className="text-emerald-400 font-bold">${item.total_spend.toFixed(2)}</div>
              <div className="text-slate-400">{item.transaction_count} transactions</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CalendarHeatmap;
