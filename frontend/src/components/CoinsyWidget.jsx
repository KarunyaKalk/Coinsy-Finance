import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { budgetsApi } from '../api/client';
import { Sparkles, MessageCircle, X, AlertTriangle } from 'lucide-react';

export const CoinsyWidget = () => {
  const { user } = useAuth();
  const [widgetData, setWidgetData] = useState(null);
  const [isOpen, setIsOpen] = useState(true);

  const fetchWidgetData = async () => {
    if (!user) return;
    try {
      const data = await budgetsApi.getCoinsyWidget(user.id);
      setWidgetData(data);
    } catch (err) {
      console.error('Error fetching Coinsy Widget status:', err);
    }
  };

  useEffect(() => {
    fetchWidgetData();
  }, [user]);

  if (!user || !widgetData) return null;

  const mood = widgetData.mascot_mood || 'happy';
  const isAlert = mood === 'concerned';

  const getMoodEmoji = (m) => {
    switch (m) {
      case 'concerned':
        return '😟';
      case 'celebrating':
        return '🎉';
      case 'sleepy':
        return '😴';
      case 'thinking':
        return '🤔';
      default:
        return '😊';
    }
  };

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col items-end">
      {/* Speech Bubble / Notification */}
      {isOpen && (
        <div
          className={`mb-3 max-w-sm w-80 bg-white border rounded-2xl shadow-xl p-4 transition-all duration-300 relative ${
            isAlert ? 'border-amber-300 ring-2 ring-amber-400/20' : 'border-slate-200'
          }`}
        >
          <button
            onClick={() => setIsOpen(false)}
            className="absolute top-2.5 right-2.5 text-slate-400 hover:text-slate-600 p-1 rounded-full hover:bg-slate-100 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>

          <div className="flex items-start space-x-3">
            <div className="text-2xl shrink-0 mt-0.5">{getMoodEmoji(mood)}</div>
            <div className="space-y-1 pr-3">
              <div className="flex items-center space-x-1.5">
                <span className="font-bold text-xs text-slate-900">Coinsy AI Assistant</span>
                {isAlert && (
                  <span className="inline-flex items-center text-[10px] bg-rose-100 text-rose-800 font-bold px-1.5 py-0.2 rounded">
                    <AlertTriangle className="w-3 h-3 mr-0.5 text-rose-600" /> Alert
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-700 leading-snug">{widgetData.message}</p>
            </div>
          </div>
        </div>
      )}

      {/* Floating Mascot Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center space-x-2 px-3.5 py-2.5 rounded-full shadow-lg transition-all duration-200 hover:scale-105 active:scale-95 text-white font-medium text-xs ${
          isAlert ? 'bg-amber-600 hover:bg-amber-700 ring-4 ring-amber-200' : 'bg-indigo-600 hover:bg-indigo-700'
        }`}
      >
        <span className="text-lg">{getMoodEmoji(mood)}</span>
        <span className="font-semibold">Coinsy</span>
        <Sparkles className="w-3.5 h-3.5 text-amber-300" />
      </button>
    </div>
  );
};

export default CoinsyWidget;
