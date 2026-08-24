import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

const CATEGORY_COLORS = {
  Food: '#EF4444',
  Transport: '#3B82F6',
  Rent: '#8B5CF6',
  Utilities: '#F59E0B',
  Shopping: '#EC4899',
  Entertainment: '#10B981',
  Subscriptions: '#6366F1',
  Investments: '#14B8A6',
  Other: '#64748B',
  Uncategorized: '#94A3B8',
};

const DEFAULT_COLORS = ['#6366F1', '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

export const CategoryDonutChart = ({ data = [], totalSpend = 0 }) => {
  if (!data || data.length === 0 || totalSpend === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 border border-dashed border-slate-200 rounded-lg text-slate-400 text-xs">
        <span>No category spend recorded for this timeframe</span>
      </div>
    );
  }

  const chartData = data.map((item) => ({
    name: item.category_name,
    value: item.total_spend,
    percentage: item.percentage_of_total,
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const info = payload[0].payload;
      return (
        <div className="bg-slate-900 text-white text-xs p-2.5 rounded-lg shadow-lg border border-slate-800 space-y-1">
          <div className="font-semibold">{info.name}</div>
          <div>Total Spend: ${info.value.toFixed(2)}</div>
          <div className="text-slate-400">{info.percentage}% of total</div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
          >
            {chartData.map((entry, index) => {
              const color = CATEGORY_COLORS[entry.name] || DEFAULT_COLORS[index % DEFAULT_COLORS.length];
              return <Cell key={`cell-${index}`} fill={color} stroke="none" />;
            })}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={36}
            iconType="circle"
            formatter={(value) => <span className="text-xs text-slate-600 font-medium">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CategoryDonutChart;
