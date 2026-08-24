import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { analyticsApi, insightsApi, transactionsApi } from '../api/client';
import CategoryDonutChart from '../components/charts/CategoryDonutChart';
import ComparisonBarChart from '../components/charts/ComparisonBarChart';
import TrendLineChart from '../components/charts/TrendLineChart';
import AuditFeed from '../components/AuditFeed';
import { TrendingUp, Lightbulb, Sparkles, Calendar, DollarSign, ArrowUpRight, ArrowDownRight, PieChartIcon, BarChart2, LineChartIcon } from 'lucide-react';

export const DashboardPage = () => {
  const { user } = useAuth();

  const [timeframe, setTimeframe] = useState('monthly'); // weekly | monthly | yearly

  const [spendData, setSpendData] = useState(null);
  const [compData, setCompData] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [tipData, setTipData] = useState(null);
  const [predictionData, setPredictionData] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  const compPeriod = timeframe === 'weekly' ? 'wow' : 'mom';

  const fetchData = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const [spend, comp, summary, tip, pred, txs] = await Promise.allSettled([
        analyticsApi.getSpend(timeframe, user.id),
        analyticsApi.getComparison(compPeriod, user.id),
        analyticsApi.getSummary(compPeriod, user.id),
        insightsApi.getDailyTip(user.id),
        insightsApi.getPrediction(user.id),
        transactionsApi.listTransactions({ user_id: user.id, limit: 10 }),
      ]);

      if (spend.status === 'fulfilled') setSpendData(spend.value);
      if (comp.status === 'fulfilled') setCompData(comp.value);
      if (summary.status === 'fulfilled') setSummaryData(summary.value);
      if (tip.status === 'fulfilled') setTipData(tip.value);
      if (pred.status === 'fulfilled') setPredictionData(pred.value);
      if (txs.status === 'fulfilled') setTransactions(txs.value);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [user, timeframe]);

  if (loading && !spendData) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500 text-sm font-medium">
        Loading interactive financial dashboard...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header & View Toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Welcome back, {user?.full_name || user?.email}!
          </h1>
          <p className="text-sm text-slate-500">
            Interactive spending analytics, period comparisons & AI forecasts.
          </p>
        </div>

        {/* Timeframe View Toggle */}
        <div className="flex items-center space-x-1 bg-white p-1 rounded-xl border border-slate-200 shadow-sm text-xs font-semibold">
          <button
            onClick={() => setTimeframe('weekly')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              timeframe === 'weekly' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Weekly View
          </button>
          <button
            onClick={() => setTimeframe('monthly')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              timeframe === 'monthly' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Monthly View
          </button>
          <button
            onClick={() => setTimeframe('yearly')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              timeframe === 'yearly' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Yearly View
          </button>
        </div>
      </div>

      {/* Daily Tip Banner */}
      {tipData && (
        <div className="bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border border-amber-200/80 rounded-xl p-4 flex items-start space-x-3">
          <div className="bg-amber-500 text-white p-2 rounded-lg shrink-0">
            <Lightbulb className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xs font-semibold uppercase text-amber-800 tracking-wider">Coinsy Daily Tip</h2>
              {tipData.is_llm_generated && (
                <span className="inline-flex items-center text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-medium">
                  <Sparkles className="w-3 h-3 mr-0.5" /> AI Generated
                </span>
              )}
            </div>
            <p className="text-sm font-medium text-slate-800 mt-0.5">{tipData.tip}</p>
          </div>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Total Current Spend */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-medium text-slate-500">
            <span>Total Spend ({compData?.target_period || timeframe})</span>
            <DollarSign className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            ${compData?.total_current_spend?.toFixed(2) || '0.00'}
          </div>
          <div className="flex items-center space-x-1 text-xs">
            {compData?.trend === 'increased' ? (
              <span className="text-rose-600 flex items-center font-semibold">
                <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
                +${compData?.total_change_amount?.toFixed(2)}{' '}
                {compData?.total_percentage_change != null && `(${compData.total_percentage_change}%)`}
              </span>
            ) : compData?.trend === 'decreased' ? (
              <span className="text-emerald-600 flex items-center font-semibold">
                <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
                -${Math.abs(compData?.total_change_amount)?.toFixed(2)}{' '}
                {compData?.total_percentage_change != null && `(${compData.total_percentage_change}%)`}
              </span>
            ) : (
              <span className="text-slate-500 font-medium">Flat vs prior period</span>
            )}
            <span className="text-slate-400">vs {compData?.prior_period}</span>
          </div>
        </div>

        {/* Prior Spend */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-medium text-slate-500">
            <span>Prior Period Spend ({compData?.prior_period || 'N/A'})</span>
            <Calendar className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            ${compData?.total_prior_spend?.toFixed(2) || '0.00'}
          </div>
          <div className="text-xs text-slate-400">Baseline for comparison</div>
        </div>

        {/* Forecasted Next Month Spend */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-medium text-slate-500">
            <span>Forecasted Spend ({predictionData?.forecast_month || 'Next Month'})</span>
            <TrendingUp className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="text-2xl font-bold text-indigo-600">
            ${predictionData?.total_predicted_spend?.toFixed(2) || '0.00'}
          </div>
          <div className="text-xs text-slate-500 line-clamp-1">
            {predictionData?.explanation || 'Linear trend prediction model'}
          </div>
        </div>
      </div>

      {/* Visual Recharts Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Donut Chart: Category Breakdown */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <PieChartIcon className="w-4 h-4 text-indigo-600" />
              <h2 className="text-base font-semibold text-slate-900">Category Breakdown</h2>
            </div>
            <span className="text-xs font-medium text-slate-500 uppercase">{timeframe} view</span>
          </div>
          <CategoryDonutChart
            data={spendData?.category_totals || []}
            totalSpend={spendData?.total_spend || 0}
          />
        </div>

        {/* Bar Chart: This Period vs Last Period Comparison */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <BarChart2 className="w-4 h-4 text-indigo-600" />
              <h2 className="text-base font-semibold text-slate-900">
                {timeframe === 'weekly' ? 'This Week vs Last Week' : 'This Month vs Last Month'}
              </h2>
            </div>
            <span className="text-xs font-medium text-slate-500 uppercase">{compPeriod.toUpperCase()} comparison</span>
          </div>
          <ComparisonBarChart
            categories={compData?.categories || []}
            targetPeriod={compData?.target_period || 'Current'}
            priorPeriod={compData?.prior_period || 'Prior'}
          />
        </div>
      </div>

      {/* Full Width Line Chart: Spend Trend Over Time */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <LineChartIcon className="w-4 h-4 text-indigo-600" />
            <h2 className="text-base font-semibold text-slate-900">Spending Trend Over Time</h2>
          </div>
          <span className="text-xs font-medium text-slate-500 uppercase">{timeframe} trend</span>
        </div>
        <TrendLineChart periods={spendData?.periods || []} />
      </div>

      {/* Module 8 Component: Transparent Agent Audit Activity Feed */}
      <AuditFeed />

      {/* Category Comparison Table & Natural Language Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-900">Category Spend Details</h2>
            <span className="text-xs font-medium text-slate-500 uppercase">
              {compPeriod.toUpperCase()} Breakdown
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Current</th>
                  <th className="py-2.5 px-3">Prior</th>
                  <th className="py-2.5 px-3">Change</th>
                  <th className="py-2.5 px-3">Trend</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {compData?.categories && compData.categories.length > 0 ? (
                  compData.categories.map((c) => (
                    <tr key={c.category_name} className="hover:bg-slate-50">
                      <td className="py-2.5 px-3 font-medium text-slate-800">{c.category_name}</td>
                      <td className="py-2.5 px-3">${c.current_spend.toFixed(2)}</td>
                      <td className="py-2.5 px-3 text-slate-400">${c.prior_spend.toFixed(2)}</td>
                      <td className="py-2.5 px-3 font-medium">
                        {c.change_amount > 0 ? (
                          <span className="text-rose-600">+${c.change_amount.toFixed(2)}</span>
                        ) : c.change_amount < 0 ? (
                          <span className="text-emerald-600">-${Math.abs(c.change_amount).toFixed(2)}</span>
                        ) : (
                          <span className="text-slate-400">$0.00</span>
                        )}
                      </td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                            c.trend === 'increased'
                              ? 'bg-rose-50 text-rose-700'
                              : c.trend === 'decreased'
                              ? 'bg-emerald-50 text-emerald-700'
                              : c.trend === 'new'
                              ? 'bg-indigo-50 text-indigo-700'
                              : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          {c.trend}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="py-6 text-center text-slate-400 text-xs">
                      No transaction records found for comparison.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Natural Language Summary Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-base font-semibold text-slate-900">Period Text Summary</h2>
              {summaryData?.is_llm_generated && (
                <span className="inline-flex items-center text-[10px] bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-medium">
                  <Sparkles className="w-3 h-3 mr-1" /> Claude AI
                </span>
              )}
            </div>
            <p className="text-sm leading-relaxed text-slate-700 bg-slate-50 border border-slate-200 p-4 rounded-lg">
              {summaryData?.summary || 'Generating summary...'}
            </p>
          </div>

          {predictionData && (
            <div className="border-t border-slate-100 pt-3 space-y-1">
              <span className="text-xs font-semibold uppercase text-slate-400">1-Line Forecast Insight</span>
              <p className="text-xs italic text-slate-600">{predictionData.explanation}</p>
            </div>
          )}
        </div>
      </div>

      {/* Recent Transactions List */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900">Recent Transactions</h2>
          <span className="text-xs text-slate-500 font-medium">Last 10 records</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">Description</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Payment</th>
                <th className="py-2.5 px-3 text-right">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {transactions.length > 0 ? (
                transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 text-slate-500">{tx.date}</td>
                    <td className="py-2.5 px-3 font-medium text-slate-800">{tx.description}</td>
                    <td className="py-2.5 px-3">
                      <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-xs">
                        {tx.category?.name || 'Uncategorized'}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 text-xs">{tx.payment_mode}</td>
                    <td
                      className={`py-2.5 px-3 text-right font-medium ${
                        tx.type === 'debit' ? 'text-slate-900' : 'text-emerald-600'
                      }`}
                    >
                      {tx.type === 'debit' ? '-' : '+'}${tx.amount.toFixed(2)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="py-6 text-center text-slate-400 text-xs">
                    No transactions found. Go to <a href="/import" className="text-indigo-600 underline">Import</a> to upload your bank statement.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
