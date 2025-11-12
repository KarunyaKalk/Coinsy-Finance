import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, PiggyBank, AlertCircle, Plus, Calendar, Target, Award, RefreshCw, Trash2, Database, BarChart3 } from 'lucide-react';

const AIPersonalFinance = () => {
  // Sample data structure
  const sampleMonthlyData = {
    '2025-01': [
      { id: 1, date: '2025-01-05', category: 'Food', amount: 450, description: 'Groceries' },
      { id: 2, date: '2025-01-08', category: 'Transport', amount: 120, description: 'Fuel' },
      { id: 3, date: '2025-01-12', category: 'Entertainment', amount: 200, description: 'Movie' },
      { id: 4, date: '2025-01-15', category: 'Bills', amount: 800, description: 'Electricity' },
      { id: 5, date: '2025-01-20', category: 'Shopping', amount: 550, description: 'Clothing' },
    ],
    '2025-02': [
      { id: 6, date: '2025-02-03', category: 'Food', amount: 520, description: 'Groceries' },
      { id: 7, date: '2025-02-07', category: 'Transport', amount: 150, description: 'Fuel' },
      { id: 8, date: '2025-02-11', category: 'Entertainment', amount: 180, description: 'Concert' },
      { id: 9, date: '2025-02-14', category: 'Food', amount: 300, description: 'Dinner' },
      { id: 10, date: '2025-02-20', category: 'Bills', amount: 850, description: 'Utilities' },
    ],
    '2025-03': [
      { id: 11, date: '2025-03-02', category: 'Food', amount: 480, description: 'Groceries' },
      { id: 12, date: '2025-03-05', category: 'Healthcare', amount: 600, description: 'Medical' },
      { id: 13, date: '2025-03-10', category: 'Transport', amount: 130, description: 'Fuel' },
      { id: 14, date: '2025-03-15', category: 'Entertainment', amount: 220, description: 'Gaming' },
      { id: 15, date: '2025-03-22', category: 'Shopping', amount: 700, description: 'Electronics' },
    ],
    '2025-04': [
      { id: 16, date: '2025-04-01', category: 'Food', amount: 510, description: 'Groceries' },
      { id: 17, date: '2025-04-08', category: 'Transport', amount: 140, description: 'Fuel' },
      { id: 18, date: '2025-04-12', category: 'Bills', amount: 780, description: 'Internet' },
      { id: 19, date: '2025-04-18', category: 'Entertainment', amount: 250, description: 'Restaurant' },
      { id: 20, date: '2025-04-25', category: 'Food', amount: 420, description: 'Groceries' },
    ],
    '2025-05': [
      { id: 21, date: '2025-05-03', category: 'Food', amount: 490, description: 'Groceries' },
      { id: 22, date: '2025-05-07', category: 'Shopping', amount: 650, description: 'Furniture' },
      { id: 23, date: '2025-05-12', category: 'Transport', amount: 160, description: 'Fuel' },
      { id: 24, date: '2025-05-18', category: 'Entertainment', amount: 190, description: 'Movies' },
      { id: 25, date: '2025-05-24', category: 'Bills', amount: 820, description: 'Utilities' },
    ],
    '2025-06': [
      { id: 26, date: '2025-06-02', category: 'Food', amount: 530, description: 'Groceries' },
      { id: 27, date: '2025-06-08', category: 'Transport', amount: 145, description: 'Fuel' },
      { id: 28, date: '2025-06-14', category: 'Healthcare', amount: 400, description: 'Pharmacy' },
      { id: 29, date: '2025-06-20', category: 'Entertainment', amount: 280, description: 'Concert' },
      { id: 30, date: '2025-06-26', category: 'Food', amount: 380, description: 'Restaurant' },
    ],
    '2025-07': [
      { id: 31, date: '2025-07-04', category: 'Food', amount: 470, description: 'Groceries' },
      { id: 32, date: '2025-07-10', category: 'Shopping', amount: 800, description: 'Appliances' },
      { id: 33, date: '2025-07-15', category: 'Transport', amount: 135, description: 'Fuel' },
      { id: 34, date: '2025-07-21', category: 'Bills', amount: 890, description: 'Electricity' },
      { id: 35, date: '2025-07-28', category: 'Entertainment', amount: 210, description: 'Sports' },
    ],
    '2025-08': [
      { id: 36, date: '2025-08-01', category: 'Food', amount: 505, description: 'Groceries' },
      { id: 37, date: '2025-08-06', category: 'Transport', amount: 155, description: 'Fuel' },
      { id: 38, date: '2025-08-12', category: 'Entertainment', amount: 240, description: 'Theater' },
      { id: 39, date: '2025-08-18', category: 'Food', amount: 350, description: 'Dining' },
      { id: 40, date: '2025-08-25', category: 'Shopping', amount: 620, description: 'Clothing' },
    ],
    '2025-09': [
      { id: 41, date: '2025-09-03', category: 'Food', amount: 485, description: 'Groceries' },
      { id: 42, date: '2025-09-09', category: 'Bills', amount: 810, description: 'Utilities' },
      { id: 43, date: '2025-09-14', category: 'Transport', amount: 148, description: 'Fuel' },
      { id: 44, date: '2025-09-20', category: 'Healthcare', amount: 550, description: 'Medical' },
      { id: 45, date: '2025-09-27', category: 'Entertainment', amount: 195, description: 'Gaming' },
    ],
    '2025-10': [
      { id: 46, date: '2025-10-01', category: 'Food', amount: 450, description: 'Groceries' },
      { id: 47, date: '2025-10-03', category: 'Transport', amount: 120, description: 'Fuel' },
      { id: 48, date: '2025-10-05', category: 'Entertainment', amount: 200, description: 'Movie & Dinner' },
      { id: 49, date: '2025-10-07', category: 'Food', amount: 380, description: 'Restaurant' },
      { id: 50, date: '2025-10-10', category: 'Bills', amount: 800, description: 'Electricity & Water' },
      { id: 51, date: '2025-10-12', category: 'Shopping', amount: 550, description: 'Clothing' },
      { id: 52, date: '2025-10-15', category: 'Food', amount: 420, description: 'Groceries' },
      { id: 53, date: '2025-10-18', category: 'Transport', amount: 150, description: 'Fuel' },
      { id: 54, date: '2025-10-20', category: 'Entertainment', amount: 180, description: 'Concert' },
      { id: 55, date: '2025-10-22', category: 'Food', amount: 90, description: 'Lunch' },
    ],
  };

  const sampleYearlyData = {
    '2023': sampleMonthlyData,
    '2024': {
      '2024-01': [{ id: 1001, date: '2024-01-10', category: 'Food', amount: 3200, description: 'Monthly Total' }],
      '2024-02': [{ id: 1002, date: '2024-02-10', category: 'Food', amount: 2980, description: 'Monthly Total' }],
      '2024-03': [{ id: 1003, date: '2024-03-10', category: 'Food', amount: 3450, description: 'Monthly Total' }],
      '2024-04': [{ id: 1004, date: '2024-04-10', category: 'Food', amount: 3100, description: 'Monthly Total' }],
      '2024-05': [{ id: 1005, date: '2024-05-10', category: 'Food', amount: 3350, description: 'Monthly Total' }],
      '2024-06': [{ id: 1006, date: '2024-06-10', category: 'Food', amount: 2950, description: 'Monthly Total' }],
      '2024-07': [{ id: 1007, date: '2024-07-10', category: 'Food', amount: 3280, description: 'Monthly Total' }],
      '2024-08': [{ id: 1008, date: '2024-08-10', category: 'Food', amount: 3150, description: 'Monthly Total' }],
      '2024-09': [{ id: 1009, date: '2024-09-10', category: 'Food', amount: 3420, description: 'Monthly Total' }],
      '2024-10': [{ id: 1010, date: '2024-10-10', category: 'Food', amount: 3200, description: 'Monthly Total' }],
      '2024-11': [{ id: 1011, date: '2024-11-10', category: 'Food', amount: 3380, description: 'Monthly Total' }],
      '2024-12': [{ id: 1012, date: '2024-12-10', category: 'Food', amount: 3600, description: 'Monthly Total' }],
    },
    '2025': sampleMonthlyData,
  };

  const [useSampleData, setUseSampleData] = useState(true);
  const [allExpenses, setAllExpenses] = useState(useSampleData ? sampleYearlyData : { '2025': { '2025-10': [] } });
  const [currentYear, setCurrentYear] = useState('2025');
  const [currentMonth, setCurrentMonth] = useState('2025-10');
  const [budget, setBudget] = useState(5000);
  const [savingsGoal, setSavingsGoal] = useState(1500);
  const [view, setView] = useState('dashboard');
  const [analyticsView, setAnalyticsView] = useState('current');
  const [newExpense, setNewExpense] = useState({
    date: new Date().toISOString().split('T')[0],
    category: 'Food',
    amount: '',
    description: ''
  });

  const categories = ['Food', 'Transport', 'Entertainment', 'Bills', 'Shopping', 'Healthcare', 'Other'];
  const categoryColors = {
    Food: '#FF6B6B',
    Transport: '#4ECDC4',
    Entertainment: '#45B7D1',
    Bills: '#FFA07A',
    Shopping: '#98D8C8',
    Healthcare: '#F7DC6F',
    Other: '#BB8FCE'
  };

  useEffect(() => {
    if (useSampleData) {
      setAllExpenses(sampleYearlyData);
    } else {
      const today = new Date();
      const yearMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
      setAllExpenses({ [today.getFullYear().toString()]: { [yearMonth]: [] } });
      setCurrentYear(today.getFullYear().toString());
      setCurrentMonth(yearMonth);
    }
  }, [useSampleData]);

  const getCurrentMonthExpenses = () => {
    return allExpenses[currentYear]?.[currentMonth] || [];
  };

  const getYearExpenses = (year) => {
    const yearData = allExpenses[year] || {};
    return Object.values(yearData).flat();
  };

  const getAllYearsExpenses = () => {
    return Object.keys(allExpenses).flatMap(year => getYearExpenses(year));
  };

  const resetMonth = () => {
    if (confirm('Are you sure you want to reset this month? This will clear all current month expenses.')) {
      const newData = { ...allExpenses };
      if (newData[currentYear]) {
        newData[currentYear][currentMonth] = [];
      }
      setAllExpenses(newData);
    }
  };

  const resetYear = () => {
    if (confirm('Are you sure you want to reset this year? This will clear all expenses for this year.')) {
      const newData = { ...allExpenses };
      newData[currentYear] = {};
      setAllExpenses(newData);
    }
  };

  const toggleSampleData = () => {
    if (!useSampleData) {
      setUseSampleData(true);
    } else {
      if (confirm('Switch to real data mode? This will clear all sample data and start fresh.')) {
        const today = new Date();
        const yearMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
        setAllExpenses({ [today.getFullYear().toString()]: { [yearMonth]: [] } });
        setCurrentYear(today.getFullYear().toString());
        setCurrentMonth(yearMonth);
        setUseSampleData(false);
      }
    }
  };

  // Calculate monthly data for yearly view
  const getMonthlyTotals = (year) => {
    const yearData = allExpenses[year] || {};
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    return months.map((month, idx) => {
      const monthKey = `${year}-${String(idx + 1).padStart(2, '0')}`;
      const expenses = yearData[monthKey] || [];
      const total = expenses.reduce((sum, e) => sum + e.amount, 0);
      return { month, amount: total };
    });
  };

  // Calculate yearly totals for multi-year view
  const getYearlyTotals = () => {
    return Object.keys(allExpenses).map(year => {
      const total = getYearExpenses(year).reduce((sum, e) => sum + e.amount, 0);
      return { year, amount: total };
    });
  };

  // Current month calculations
  const expenses = getCurrentMonthExpenses();
  const totalSpent = expenses.reduce((sum, e) => sum + e.amount, 0);
  const remainingBudget = budget - totalSpent;
  const budgetUsedPercent = (totalSpent / budget) * 100;

  // Category spending
  const categorySpending = categories.map(cat => {
    let total = 0;
    if (analyticsView === 'current') {
      total = expenses.filter(e => e.category === cat).reduce((sum, e) => sum + e.amount, 0);
    } else if (analyticsView === 'yearly') {
      total = getYearExpenses(currentYear).filter(e => e.category === cat).reduce((sum, e) => sum + e.amount, 0);
    } else {
      total = getAllYearsExpenses().filter(e => e.category === cat).reduce((sum, e) => sum + e.amount, 0);
    }
    return { category: cat, amount: total };
  }).filter(c => c.amount > 0);

  // Trend data
  const getTrendData = () => {
    if (analyticsView === 'current') {
      const last7Days = [...Array(7)].map((_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (6 - i));
        return date.toISOString().split('T')[0];
      });
      return last7Days.map(date => {
        const dayExpenses = expenses.filter(e => e.date === date).reduce((sum, e) => sum + e.amount, 0);
        return {
          date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          amount: dayExpenses
        };
      });
    } else if (analyticsView === 'yearly') {
      return getMonthlyTotals(currentYear);
    } else {
      return getYearlyTotals();
    }
  };

  const trendData = getTrendData();

  // Predictive analytics
  const averageDailySpending = totalSpent / new Date().getDate();
  const predictedMonthlySpending = Math.round(averageDailySpending * 30);
  const predictedSavings = budget - predictedMonthlySpending;

  const recentSpending = expenses.slice(-5).reduce((sum, e) => sum + e.amount, 0) / Math.max(1, expenses.slice(-5).length);
  const olderSpending = expenses.slice(0, 5).reduce((sum, e) => sum + e.amount, 0) / Math.max(1, expenses.slice(0, 5).length);
  const spendingTrend = olderSpending > 0 ? ((recentSpending - olderSpending) / olderSpending) * 100 : 0;

  const getSmartReminders = () => {
    const reminders = [];
    
    if (budgetUsedPercent > 80) {
      reminders.push({
        type: 'warning',
        message: `You've used ${budgetUsedPercent.toFixed(0)}% of your budget. Consider reducing discretionary spending.`,
        icon: AlertCircle
      });
    }

    if (spendingTrend > 20) {
      reminders.push({
        type: 'alert',
        message: `Your spending has increased by ${spendingTrend.toFixed(0)}% recently. Review your recent purchases.`,
        icon: TrendingUp
      });
    }

    const foodSpending = categorySpending.find(c => c.category === 'Food')?.amount || 0;
    if (foodSpending > budget * 0.3) {
      reminders.push({
        type: 'tip',
        message: `Food expenses are ${((foodSpending/budget)*100).toFixed(0)}% of budget. Meal planning could save ₹${Math.round(foodSpending * 0.2)}/month.`,
        icon: Target
      });
    }

    if (predictedSavings > savingsGoal) {
      reminders.push({
        type: 'success',
        message: `Great job! You're on track to exceed your savings goal by ₹${Math.round(predictedSavings - savingsGoal)}.`,
        icon: Award
      });
    }

    return reminders;
  };

  const addExpense = () => {
    if (newExpense.amount && newExpense.description) {
      const expenseDate = new Date(newExpense.date);
      const year = expenseDate.getFullYear().toString();
      const month = `${year}-${String(expenseDate.getMonth() + 1).padStart(2, '0')}`;
      
      const newData = { ...allExpenses };
      if (!newData[year]) newData[year] = {};
      if (!newData[year][month]) newData[year][month] = [];
      
      const newId = Math.max(0, ...Object.values(newData).flatMap(y => Object.values(y).flatMap(m => m.map(e => e.id)))) + 1;
      
      newData[year][month] = [...newData[year][month], {
        id: newId,
        ...newExpense,
        amount: parseFloat(newExpense.amount)
      }];
      
      setAllExpenses(newData);
      setCurrentYear(year);
      setCurrentMonth(month);
      
      setNewExpense({
        date: new Date().toISOString().split('T')[0],
        category: 'Food',
        amount: '',
        description: ''
      });
      setView('dashboard');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 border border-indigo-100">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                AI Finance Assistant
              </h1>
              <p className="text-gray-600 mt-2">Smart budgeting with predictive insights</p>
            </div>
            <div className="flex gap-3 flex-wrap">
              <button
                onClick={toggleSampleData}
                className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                  useSampleData 
                    ? 'bg-amber-100 text-amber-700 hover:bg-amber-200' 
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                }`}
              >
                <Database size={18} />
                {useSampleData ? 'Using Sample Data' : 'Real Data Mode'}
              </button>
              <button
                onClick={() => setView('dashboard')}
                className={`px-6 py-2 rounded-lg font-medium transition-all ${
                  view === 'dashboard' 
                    ? 'bg-indigo-600 text-white shadow-lg' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setView('add')}
                className={`px-6 py-2 rounded-lg font-medium transition-all ${
                  view === 'add' 
                    ? 'bg-indigo-600 text-white shadow-lg' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Add Expense
              </button>
            </div>
          </div>
        </div>

        {view === 'dashboard' ? (
          <>
            {/* Analytics View Selector */}
            <div className="bg-white rounded-2xl shadow-lg p-4 mb-6 border border-indigo-100">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex gap-2">
                  <button
                    onClick={() => setAnalyticsView('current')}
                    className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                      analyticsView === 'current' 
                        ? 'bg-indigo-600 text-white' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <Calendar size={18} />
                    Current Month
                  </button>
                  <button
                    onClick={() => setAnalyticsView('yearly')}
                    className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                      analyticsView === 'yearly' 
                        ? 'bg-indigo-600 text-white' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <BarChart3 size={18} />
                    Year {currentYear}
                  </button>
                  <button
                    onClick={() => setAnalyticsView('alltime')}
                    className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                      analyticsView === 'alltime' 
                        ? 'bg-indigo-600 text-white' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <TrendingUp size={18} />
                    All Years
                  </button>
                </div>
                <div className="flex gap-2">
                  {analyticsView === 'current' && (
                    <button
                      onClick={resetMonth}
                      className="px-4 py-2 rounded-lg font-medium bg-orange-100 text-orange-700 hover:bg-orange-200 transition-all flex items-center gap-2"
                    >
                      <RefreshCw size={18} />
                      Reset Month
                    </button>
                  )}
                  {analyticsView === 'yearly' && (
                    <button
                      onClick={resetYear}
                      className="px-4 py-2 rounded-lg font-medium bg-red-100 text-red-700 hover:bg-red-200 transition-all flex items-center gap-2"
                    >
                      <Trash2 size={18} />
                      Reset Year
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Key Metrics */}
            {analyticsView === 'current' && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                  <div className="bg-white rounded-2xl shadow-lg p-6 border border-indigo-100">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm font-medium">Total Spent</p>
                        <p className="text-3xl font-bold text-gray-900 mt-1">₹{totalSpent}</p>
                      </div>
                      <div className="bg-red-100 p-3 rounded-xl">
                        <DollarSign className="text-red-600" size={28} />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center text-sm">
                      <span className={`font-medium ${budgetUsedPercent > 80 ? 'text-red-600' : 'text-green-600'}`}>
                        {budgetUsedPercent.toFixed(1)}% of budget
                      </span>
                    </div>
                  </div>

                  <div className="bg-white rounded-2xl shadow-lg p-6 border border-indigo-100">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm font-medium">Remaining</p>
                        <p className="text-3xl font-bold text-gray-900 mt-1">₹{remainingBudget}</p>
                      </div>
                      <div className="bg-green-100 p-3 rounded-xl">
                        <PiggyBank className="text-green-600" size={28} />
                      </div>
                    </div>
                    <div className="mt-4 text-sm text-gray-600">
                      Budget: ₹{budget}
                    </div>
                  </div>

                  <div className="bg-white rounded-2xl shadow-lg p-6 border border-indigo-100">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm font-medium">Predicted Spending</p>
                        <p className="text-3xl font-bold text-gray-900 mt-1">₹{predictedMonthlySpending}</p>
                      </div>
                      <div className="bg-blue-100 p-3 rounded-xl">
                        <TrendingUp className="text-blue-600" size={28} />
                      </div>
                    </div>
                    <div className="mt-4 text-sm text-gray-600">
                      Next 30 days forecast
                    </div>
                  </div>

                  <div className="bg-white rounded-2xl shadow-lg p-6 border border-indigo-100">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm font-medium">Projected Savings</p>
                        <p className="text-3xl font-bold text-gray-900 mt-1">₹{Math.max(0, predictedSavings)}</p>
                      </div>
                      <div className={`p-3 rounded-xl ${predictedSavings >= savingsGoal ? 'bg-green-100' : 'bg-orange-100'}`}>
                        <Target className={predictedSavings >= savingsGoal ? 'text-green-600' : 'text-orange-600'} size={28} />
                      </div>
                    </div>
                    <div className="mt-4 text-sm text-gray-600">
                      Goal: ₹{savingsGoal}
                    </div>
                  </div>
                </div>

                {/* Smart Reminders */}
                <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 border border-indigo-100">
                  <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <AlertCircle className="text-indigo-600" size={24} />
                    Smart Insights & Reminders
                  </h2>
                  <div className="space-y-3">
                    {getSmartReminders().map((reminder, idx) => (
                      <div 
                        key={idx}
                        className={`p-4 rounded-xl border-l-4 ${
                          reminder.type === 'warning' ? 'bg-orange-50 border-orange-500' :
                          reminder.type === 'alert' ? 'bg-red-50 border-red-500' :
                          reminder.type === 'success' ? 'bg-green-50 border-green-500' :
                          'bg-blue-50 border-blue-500'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <reminder.icon className={`mt-1 ${
                            reminder.type === 'warning' ? 'text-orange-600' :
                            reminder.type === 'alert' ? 'text-red-600' :
                            reminder.type === 'success' ? 'text-green-600' :
                            'text-blue-600'
                          }`} size={20} />
                          <p className="text-gray-800 flex-1">{reminder.message}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* Summary Cards for Yearly and All-time */}
            {(analyticsView === 'yearly' || analyticsView === 'alltime') && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="bg-white rounded-2xl shadow-lg p-6 border border-indigo-100">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-600 text-sm font-medium">
                        {analyticsView === 'yearly' ? `Total Spent in ${currentYear}` : 'Total Spent All Time'}
                      </p>
                      <p className="text-3xl font-bold text-gray-900 mt-1">
                        ₹{analyticsView === 'yearly' 
                          ? getYearExpenses(currentYear).reduce((sum, e) => sum + e.amount, 0)
                          : getAllYearsExpenses().reduce((sum, e) => sum + e.amount, 0)
                        }
                      </p>
                    </div>
                    <div className="bg-indigo-100 p-3 rounded-xl">
                      <DollarSign className="text-indigo-600" size={28} />
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-2xl shadow-lg p-6 border border-indigo-100">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-600 text-sm font-medium">Average per Month</p>
                      <p className="text-3xl font-bold text-gray-900 mt-1">
                        ₹{analyticsView === 'yearly' 
                          ? Math.round(getMonthlyTotals(currentYear).reduce((sum, m) => sum + m.amount, 0) / 12)
                          : Math.round(getAllYearsExpenses().reduce((sum, e) => sum + e.amount, 0) / (Object.keys(allExpenses).length * 12))
                        }
                      </p>
                    </div>
                    <div className="bg-purple-100 p-3 rounded-xl">
                      <BarChart3 className="text-purple-600" size={28} />
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-2xl shadow-lg p-6 border border-indigo-100">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-600 text-sm font-medium">
                        {analyticsView === 'yearly' ? 'Months Tracked' : 'Years Tracked'}
                      </p>
                      <p className="text-3xl font-bold text-gray-900 mt-1">
                        {analyticsView === 'yearly' 
                          ? Object.keys(allExpenses[currentYear] || {}).length
                          : Object.keys(allExpenses).length
                        }
                      </p>
                    </div>
                    <div className="bg-teal-100 p-3 rounded-xl">
                      <Calendar className="text-teal-600" size={28} />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Spending Trend */}
              <div className="bg-white rounded-2xl shadow-lg p-6 border border-indigo-100">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  {analyticsView === 'current' && 'Spending Trend (Last 7 Days)'}
                  {analyticsView === 'yearly' && `Monthly Spending in ${currentYear}`}
                  {analyticsView === 'alltime' && 'Yearly Spending Comparison'}
                </h2>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={trendData}>
                    <defs>
                      <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey={analyticsView === 'current' ? 'date' : analyticsView === 'yearly' ? 'month' : 'year'} 
                      stroke="#666" 
                    />
                    <YAxis stroke="#666" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                      formatter={(value) => `₹${value}`}
                    />
                    <Area type="monotone" dataKey="amount" stroke="#6366f1" fillOpacity={1} fill="url(#colorAmount)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Category Breakdown */}
              <div className="bg-white rounded-2xl shadow-lg p-6 border border-indigo-100">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  Spending by Category
                  {analyticsView === 'yearly' && ` (${currentYear})`}
                  {analyticsView === 'alltime' && ' (All Time)'}
                </h2>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={categorySpending}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({category, percent}) => `${category} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="amount"
                    >
                      {categorySpending.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={categoryColors[entry.category]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `₹${value}`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Category Details */}
            <div className="bg-white rounded-2xl shadow-lg p-6 border border-indigo-100 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Category Analysis
                {analyticsView === 'yearly' && ` (${currentYear})`}
                {analyticsView === 'alltime' && ' (All Time)'}
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categorySpending}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="category" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                    formatter={(value) => `₹${value}`}
                  />
                  <Bar dataKey="amount" radius={[8, 8, 0, 0]}>
                    {categorySpending.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={categoryColors[entry.category]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Recent Transactions */}
            {analyticsView === 'current' && (
              <div className="bg-white rounded-2xl shadow-lg p-6 border border-indigo-100">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Transactions</h2>
                {expenses.length > 0 ? (
                  <div className="space-y-3">
                    {expenses.slice(-5).reverse().map(expense => (
                      <div key={expense.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                        <div className="flex items-center gap-4">
                          <div 
                            className="w-12 h-12 rounded-xl flex items-center justify-center"
                            style={{ backgroundColor: categoryColors[expense.category] + '20' }}
                          >
                            <DollarSign style={{ color: categoryColors[expense.category] }} size={24} />
                          </div>
                          <div>
                            <p className="font-semibold text-gray-900">{expense.description}</p>
                            <p className="text-sm text-gray-600">{expense.category} • {new Date(expense.date).toLocaleDateString()}</p>
                          </div>
                        </div>
                        <p className="text-xl font-bold text-gray-900">₹{expense.amount}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <p>No transactions yet. Add your first expense to get started!</p>
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-indigo-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Add New Expense</h2>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                <input
                  type="date"
                  value={newExpense.date}
                  onChange={(e) => setNewExpense({...newExpense, date: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select
                  value={newExpense.category}
                  onChange={(e) => setNewExpense({...newExpense, category: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Amount (₹)</label>
                <input
                  type="number"
                  value={newExpense.amount}
                  onChange={(e) => setNewExpense({...newExpense, amount: e.target.value})}
                  placeholder="0.00"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <input
                  type="text"
                  value={newExpense.description}
                  onChange={(e) => setNewExpense({...newExpense, description: e.target.value})}
                  placeholder="What did you spend on?"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              
              <button
                onClick={addExpense}
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 rounded-xl font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
              >
                <Plus size={20} />
                Add Expense
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIPersonalFinance;