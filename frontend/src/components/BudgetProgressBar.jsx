import React from 'react';
import { AlertTriangle, AlertCircle, CheckCircle, Trash2 } from 'lucide-react';

export const BudgetProgressBar = ({
  id,
  categoryName,
  currentSpent = 0,
  amountLimit = 0,
  percentageUsed = 0,
  status = 'normal',
  onDelete,
}) => {
  const remaining = amountLimit - currentSpent;
  const isOver = status === 'exceeded' || percentageUsed >= 100;
  const isWarning = status === 'warning' || (percentageUsed >= 80 && percentageUsed < 100);

  // Cap width at 100% for progress bar container
  const barWidth = Math.min(percentageUsed, 100);

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-slate-800 text-sm">{categoryName}</span>

          {isOver ? (
            <span className="inline-flex items-center text-[10px] font-bold bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full">
              <AlertCircle className="w-3 h-3 mr-1 shrink-0 text-rose-600" />
              100% OVER BUDGET
            </span>
          ) : isWarning ? (
            <span className="inline-flex items-center text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">
              <AlertTriangle className="w-3 h-3 mr-1 shrink-0 text-amber-600" />
              80% NEAR LIMIT
            </span>
          ) : (
            <span className="inline-flex items-center text-[10px] font-medium bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full">
              <CheckCircle className="w-3 h-3 mr-1 shrink-0 text-emerald-600" />
              ON TRACK
            </span>
          )}
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <span className="font-bold text-slate-900">${currentSpent.toFixed(2)}</span>
          <span className="text-slate-400">/ ${amountLimit.toFixed(2)}</span>
          {onDelete && (
            <button
              onClick={() => onDelete(id)}
              className="text-slate-400 hover:text-rose-600 transition-colors p-1 rounded hover:bg-slate-100"
              title="Delete budget limit"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar Container */}
      <div className="space-y-1">
        <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden relative">
          {/* 80% Threshold Marker Line */}
          <div className="absolute top-0 bottom-0 left-[80%] w-0.5 bg-slate-300 z-10 opacity-70" title="80% Warning Threshold" />

          <div
            className={`h-full rounded-full transition-all duration-500 ${
              isOver ? 'bg-rose-600' : isWarning ? 'bg-amber-500' : 'bg-emerald-500'
            }`}
            style={{ width: `${barWidth}%` }}
          />
        </div>

        <div className="flex justify-between text-[11px] text-slate-500">
          <span>{percentageUsed.toFixed(1)}% used</span>
          <span>
            {remaining >= 0 ? (
              <span className="text-slate-600 font-medium">${remaining.toFixed(2)} left</span>
            ) : (
              <span className="text-rose-600 font-semibold">${Math.abs(remaining).toFixed(2)} over limit</span>
            )}
          </span>
        </div>
      </div>
    </div>
  );
};

export default BudgetProgressBar;
