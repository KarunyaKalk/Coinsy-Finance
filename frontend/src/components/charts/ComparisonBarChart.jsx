import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export const ComparisonBarChart = ({ categories = [], targetPeriod = 'Current', priorPeriod = 'Prior' }) => {
  if (!categories || categories.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 border border-dashed border-slate-200 rounded-lg text-slate-400 text-xs">
        <span>No comparison data available for selected period</span>
      </div>
    );
  }

  const chartData = categories.map((cat) => ({
    name: cat.category_name,
    Current: cat.current_spend,
    Prior: cat.prior_spend,
    change: cat.change_amount,
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const current = payload.find((p) => p.dataKey === 'Current')?.value || 0;
      const prior = payload.find((p) => p.dataKey === 'Prior')?.value || 0;
      const diff = current - prior;

      return (
        <div className="bg-slate-900 text-white text-xs p-2.5 rounded-lg shadow-lg border border-slate-800 space-y-1">
          <div className="font-semibold text-slate-200">{label}</div>
          <div className="text-indigo-300">
            {targetPeriod}: ${current.toFixed(2)}
          </div>
          <div className="text-slate-400">
            {priorPeriod}: ${prior.toFixed(2)}
          </div>
          <div className={`font-semibold pt-1 ${diff > 0 ? 'text-rose-400' : diff < 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
            Diff: {diff > 0 ? '+' : ''}${diff.toFixed(2)}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 11, fill: '#64748B' }}
            interval={0}
            angle={-20}
            textAnchor="end"
          />
          <YAxis tick={{ fontSize: 11, fill: '#64748B' }} tickFormatter={(val) => `$${val}`} />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            height={30}
            iconType="circle"
            formatter={(value) => (
              <span className="text-xs text-slate-600 font-medium">
                {value === 'Current' ? targetPeriod : priorPeriod}
              </span>
            )}
          />
          <Bar dataKey="Current" fill="#6366F1" radius={[4, 4, 0, 0]} maxBarSize={32} />
          <Bar dataKey="Prior" fill="#CBD5E1" radius={[4, 4, 0, 0]} maxBarSize={32} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ComparisonBarChart;
