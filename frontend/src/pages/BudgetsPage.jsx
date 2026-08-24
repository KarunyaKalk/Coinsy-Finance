import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { budgetsApi, categoriesApi, analyticsApi } from '../api/client';
import BudgetProgressBar from '../components/BudgetProgressBar';
import CalendarHeatmap from '../components/CalendarHeatmap';
import CashFlowChart from '../components/charts/CashFlowChart';
import { Target, Plus, Calendar, Flame, DollarSign, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

export const BudgetsPage = () => {
  const { user } = useAuth();

  const [budgets, setBudgets] = useState([]);
  const [categories, setCategories] = useState([]);
  const [heatmapData, setHeatmapData] = useState([]);
  const [cashflowData, setCashflowData] = useState(null);
  const [loading, setLoading] = useState(true);

  // New budget form state
  const [selectedCategory, setSelectedCategory] = useState('');
  const [amountLimit, setAmountLimit] = useState('');
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [year, setYear] = useState(new Date().getFullYear());
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  const loadData = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const [budgetsRes, categoriesRes, heatmapRes, cashflowRes] = await Promise.allSettled([
        budgetsApi.getBudgets(user.id, month, year),
        categoriesApi.listCategories(user.id),
        analyticsApi.getHeatmap(user.id, 90),
        analyticsApi.getCashFlow(user.id, 'monthly'),
      ]);

      if (budgetsRes.status === 'fulfilled') setBudgets(budgetsRes.value);
      if (categoriesRes.status === 'fulfilled') setCategories(categoriesRes.value);
      if (heatmapRes.status === 'fulfilled') setHeatmapData(heatmapRes.value);
      if (cashflowRes.status === 'fulfilled') setCashflowData(cashflowRes.value);
    } catch (err) {
      console.error('Error loading budget data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user, month, year]);

  const handleAddBudget = async (e) => {
    e.preventDefault();
    setFormError('');
    if (!selectedCategory || !amountLimit || parseFloat(amountLimit) <= 0) {
      setFormError('Please select a category and enter a valid positive budget limit.');
      return;
    }

    setIsSubmitting(true);
    try {
      await budgetsApi.setBudget(user.id, {
        category_id: parseInt(selectedCategory),
        amount_limit: parseFloat(amountLimit),
        month: parseInt(month),
        year: parseInt(year),
      });
      setAmountLimit('');
      loadData();
    } catch (err) {
      console.error('Error setting budget:', err);
      setFormError(err.response?.data?.detail || 'Failed to save budget limit.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteBudget = async (budgetId) => {
    try {
      await budgetsApi.deleteBudget(user.id, budgetId);
      loadData();
    } catch (err) {
      console.error('Error deleting budget:', err);
    }
  };

  const totalBudgeted = budgets.reduce((acc, b) => acc + b.amount_limit, 0);
  const totalSpent = budgets.reduce((acc, b) => acc + b.current_spent, 0);
  const exceededCount = budgets.filter((b) => b.status === 'exceeded').length;
  const warningCount = budgets.filter((b) => b.status === 'warning').length;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Budget Goals & Cash Flow</h1>
        <p className="text-sm text-slate-500">
          Set monthly spending caps, monitor 80%/100% threshold alerts, and track cash flow over time.
        </p>
      </div>

      {/* Summary KPI Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-3">
          <div className="bg-indigo-50 text-indigo-600 p-2.5 rounded-lg shrink-0">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs text-slate-500 font-medium block">Total Monthly Budget</span>
            <span className="text-lg font-bold text-slate-900">${totalBudgeted.toFixed(2)}</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-3">
          <div className="bg-emerald-50 text-emerald-600 p-2.5 rounded-lg shrink-0">
            <DollarSign className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs text-slate-500 font-medium block">Budgeted Spend</span>
            <span className="text-lg font-bold text-slate-900">${totalSpent.toFixed(2)}</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-3">
          <div className="bg-amber-50 text-amber-600 p-2.5 rounded-lg shrink-0">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs text-slate-500 font-medium block">80% Threshold Warnings</span>
            <span className="text-lg font-bold text-amber-600">{warningCount} Categories</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-3">
          <div className="bg-rose-50 text-rose-600 p-2.5 rounded-lg shrink-0">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs text-slate-500 font-medium block">100% Exceeded Limits</span>
            <span className="text-lg font-bold text-rose-600">{exceededCount} Categories</span>
          </div>
        </div>
      </div>

      {/* Main Budget Goals & Form Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Set Budget Form */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4 h-fit">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Plus className="w-4 h-4 text-indigo-600" />
            <h2 className="text-base font-semibold text-slate-900">Set Monthly Category Cap</h2>
          </div>

          {formError && (
            <div className="text-xs text-rose-600 bg-rose-50 border border-rose-200 p-2.5 rounded-lg">
              {formError}
            </div>
          )}

          <form onSubmit={handleAddBudget} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
              >
                <option value="">-- Select Category --</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Monthly Limit ($)
              </label>
              <input
                type="number"
                step="0.01"
                min="1"
                value={amountLimit}
                onChange={(e) => setAmountLimit(e.target.value)}
                placeholder="e.g. 500.00"
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Month</label>
                <select
                  value={month}
                  onChange={(e) => setMonth(parseInt(e.target.value))}
                  className="w-full px-2 py-2 border border-slate-300 rounded-lg text-sm bg-white"
                >
                  {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                    <option key={m} value={m}>
                      {new Date(2000, m - 1, 1).toLocaleString('default', { month: 'short' })}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Year</label>
                <input
                  type="number"
                  value={year}
                  onChange={(e) => setYear(parseInt(e.target.value))}
                  className="w-full px-2 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
            >
              {isSubmitting ? 'Saving Limit...' : 'Save Budget Goal'}
            </button>
          </form>
        </div>

        {/* Budget Progress Bars List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-900">
              Active Category Budgets ({new Date(2000, month - 1, 1).toLocaleString('default', { month: 'long' })} {year})
            </h2>
            <span className="text-xs text-slate-500">{budgets.length} goals set</span>
          </div>

          {loading ? (
            <div className="text-xs text-slate-400 py-8 text-center">Loading budget goals...</div>
          ) : budgets.length > 0 ? (
            <div className="space-y-3">
              {budgets.map((b) => (
                <BudgetProgressBar
                  key={b.id}
                  id={b.id}
                  categoryName={b.category_name}
                  currentSpent={b.current_spent}
                  amountLimit={b.amount_limit}
                  percentageUsed={b.percentage_used}
                  status={b.status}
                  onDelete={handleDeleteBudget}
                />
              ))}
            </div>
          ) : (
            <div className="border border-dashed border-slate-200 rounded-xl p-8 text-center space-y-2 bg-white">
              <Target className="w-8 h-8 text-slate-300 mx-auto" />
              <p className="text-sm font-medium text-slate-700">No monthly budgets configured yet</p>
              <p className="text-xs text-slate-400">
                Use the form on the left to set spending caps per category and receive 80%/100% threshold alerts.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Cash Flow View Section */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-indigo-600" />
            <h2 className="text-base font-semibold text-slate-900">Cash Flow Analytics (Income vs Expense vs Savings)</h2>
          </div>
          {cashflowData && (
            <div className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-md">
              Avg Savings Rate: {cashflowData.avg_savings_rate}%
            </div>
          )}
        </div>

        <CashFlowChart data={cashflowData?.periods || []} />
      </div>

      {/* Daily Spend Calendar Heatmap Section */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-center space-x-2">
          <Flame className="w-5 h-5 text-rose-500" />
          <h2 className="text-base font-semibold text-slate-900">Daily Spend Intensity Calendar Heatmap</h2>
        </div>

        <CalendarHeatmap items={heatmapData} />
      </div>
    </div>
  );
};

export default BudgetsPage;
