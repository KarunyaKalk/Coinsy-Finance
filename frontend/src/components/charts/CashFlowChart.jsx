import React from 'react';
import { ResponsiveContainer, ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export const CashFlowChart = ({ data = [], timeframe = 'monthly' }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 border border-dashed border-slate-200 rounded-lg text-slate-400 text-xs">
        No cash flow data recorded (Income vs Expense)
      </div>
    );
  }

  const chartData = data.map((item) => ({
    period: item.period,
    Income: item.income,
    Expense: item.expense,
    Savings: item.savings,
    rate: item.savings_rate,
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const inc = payload.find((p) => p.dataKey === 'Income')?.value || 0;
      const exp = payload.find((p) => p.dataKey === 'Expense')?.value || 0;
      const sav = payload.find((p) => p.dataKey === 'Savings')?.value || 0;
      const rate = inc > 0 ? ((sav / inc) * 100).toFixed(1) : 0;

      return (
        <div className="bg-slate-900 text-white text-xs p-3 rounded-lg shadow-lg border border-slate-800 space-y-1">
          <div className="font-semibold text-slate-300">{label} Cash Flow</div>
          <div className="text-emerald-400 font-medium">Income: +${inc.toFixed(2)}</div>
          <div className="text-rose-400 font-medium">Expense: -${exp.toFixed(2)}</div>
          <div className="text-indigo-400 font-bold border-t border-slate-800 pt-1">
            Net Savings: ${sav.toFixed(2)} ({rate}%)
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
          <XAxis dataKey="period" tick={{ fontSize: 11, fill: '#64748B' }} />
          <YAxis tick={{ fontSize: 11, fill: '#64748B' }} tickFormatter={(val) => `$${val}`} />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            height={30}
            iconType="circle"
            formatter={(value) => <span className="text-xs text-slate-600 font-medium">{value}</span>}
          />
          <Bar dataKey="Income" fill="#10B981" radius={[4, 4, 0, 0]} maxBarSize={28} />
          <Bar dataKey="Expense" fill="#EF4444" radius={[4, 4, 0, 0]} maxBarSize={28} />
          <Line type="monotone" dataKey="Savings" stroke="#6366F1" strokeWidth={2.5} dot={{ r: 4 }} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CashFlowChart;
