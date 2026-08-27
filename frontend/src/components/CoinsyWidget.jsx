import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { budgetsApi, insightsApi } from '../api/client';
import CoinsyMascotAvatar from './CoinsyMascotAvatar';
import { Sparkles, X, Send, Bot, User as UserIcon, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const CoinsyWidget = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [widgetData, setWidgetData] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isWiggling, setIsWiggling] = useState(false);
  const [isWelcome, setIsWelcome] = useState(true);

  // Onboarding sequence state
  const [onboardingStep, setOnboardingStep] = useState(() => {
    const savedStep = localStorage.getItem('coinsy_onboarding_step');
    return savedStep ? parseInt(savedStep) : 1;
  });
  const [onboardingDone, setOnboardingDone] = useState(() => {
    return localStorage.getItem('coinsy_onboarding_done') === 'true';
  });

  // Chat log state
  const [chatMessages, setChatMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isAsking, setIsAsking] = useState(false);
  const [currentMood, setCurrentMood] = useState('happy');

  // Setting check: Reduce Coinsy
  const reduceCoinsy = localStorage.getItem('coinsy_reduce_notifications') === 'true';

  const fetchWidgetData = async () => {
    if (!user) return;
    try {
      const data = await budgetsApi.getCoinsyWidget(user.id);
      setWidgetData(data);
      if (data.mascot_mood) {
        setCurrentMood(data.mascot_mood);
      }
      // Auto open bubble if not in reduced mode and not onboarding done
      if (!reduceCoinsy && !onboardingDone) {
        setIsOpen(true);
      }
    } catch (err) {
      console.error('Error fetching Coinsy Widget status:', err);
    }
  };

  useEffect(() => {
    fetchWidgetData();
    // Clear welcome animation after 3 seconds
    const timer = setTimeout(() => setIsWelcome(false), 3000);
    return () => clearTimeout(timer);
  }, [user]);

  const handleMascotClick = () => {
    // Click-to-wiggle interaction
    setIsWiggling(true);
    setTimeout(() => setIsWiggling(false), 600);
    setIsOpen((prev) => !prev);
  };

  const handleAskCoinsy = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isAsking) return;

    const userText = inputMessage.trim();
    setInputMessage('');
    setIsAsking(true);
    setCurrentMood('thinking');

    // Append user message to chat log
    setChatMessages((prev) => [...prev, { sender: 'user', text: userText }]);

    try {
      const roastMode = localStorage.getItem('coinsy_roast_mode') === 'true';
      const response = await insightsApi.askCoinsy({
        user_id: user.id,
        message: userText,
        roast_mode: roastMode,
      });

      setChatMessages((prev) => [
        ...prev,
        { sender: 'coinsy', text: response.reply, mood: response.mascot_mood },
      ]);
      setCurrentMood(response.mascot_mood || 'happy');
    } catch (err) {
      console.error('Error asking Coinsy:', err);
      setChatMessages((prev) => [
        ...prev,
        { sender: 'coinsy', text: 'I am tracking your finances! Feel free to ask about your budgets or spending trends.', mood: 'happy' },
      ]);
      setCurrentMood('happy');
    } finally {
      setIsAsking(false);
    }
  };

  const nextOnboardingStep = (nextStep) => {
    if (nextStep > 3) {
      setOnboardingDone(true);
      localStorage.setItem('coinsy_onboarding_done', 'true');
    } else {
      setOnboardingStep(nextStep);
      localStorage.setItem('coinsy_onboarding_step', nextStep.toString());
    }
  };

  if (!user) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col items-end">
      {/* Expandable Speech Bubble & Companion Panel */}
      {isOpen && (
        <div className="mb-3 max-w-sm w-88 bg-white border border-slate-200 rounded-2xl shadow-2xl overflow-hidden transition-all duration-300 animate-in fade-in slide-in-from-bottom-4">
          {/* Panel Header */}
          <div className="bg-slate-900 text-white px-4 py-3 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span className="font-bold text-xs">Coinsy AI Companion</span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-slate-400 hover:text-white p-1 rounded-md transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="p-4 space-y-4 max-h-96 overflow-y-auto">
            {/* Onboarding Sequence Banner */}
            {!onboardingDone && (
              <div className="bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-100 p-3.5 rounded-xl space-y-2">
                {onboardingStep === 1 && (
                  <>
                    <div className="flex items-center space-x-2 text-indigo-900 font-bold text-xs">
                      <span>Step 1: Meet Coinsy</span>
                    </div>
                    <p className="text-xs text-indigo-950 leading-relaxed">
                      "Hi! I'm Coinsy, your AI personal finance mascot! I will help you track statements, auto-categorize expenses, and stay within your budget caps."
                    </p>
                    <button
                      onClick={() => nextOnboardingStep(2)}
                      className="flex items-center space-x-1 text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-lg transition-colors"
                    >
                      <span>Next: Import Statement</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </>
                )}

                {onboardingStep === 2 && (
                  <>
                    <div className="flex items-center space-x-2 text-indigo-900 font-bold text-xs">
                      <span>Step 2: Upload Your First Statement</span>
                    </div>
                    <p className="text-xs text-indigo-950 leading-relaxed">
                      "Head over to the Import page to upload your CSV or PDF bank statement. I'll automatically parse and categorize your expenses!"
                    </p>
                    <div className="flex items-center space-x-2 pt-1">
                      <button
                        onClick={() => {
                          navigate('/import');
                          nextOnboardingStep(3);
                        }}
                        className="text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-lg transition-colors"
                      >
                        Go to Import Page
                      </button>
                      <button
                        onClick={() => nextOnboardingStep(3)}
                        className="text-xs text-indigo-700 hover:underline font-medium"
                      >
                        Skip
                      </button>
                    </div>
                  </>
                )}

                {onboardingStep === 3 && (
                  <>
                    <div className="flex items-center space-x-2 text-indigo-900 font-bold text-xs">
                      <span>Step 3: Set Monthly Budget Caps</span>
                    </div>
                    <p className="text-xs text-indigo-950 leading-relaxed">
                      "Set your category budget limits on the Budgets page. I will watch your thresholds and alert you at 80% and 100% caps!"
                    </p>
                    <div className="flex items-center space-x-2 pt-1">
                      <button
                        onClick={() => {
                          navigate('/budgets');
                          nextOnboardingStep(4);
                        }}
                        className="text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-lg transition-colors flex items-center space-x-1"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Finish Onboarding</span>
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}

            {/* Contextual Proactive Alert Message */}
            {widgetData && (
              <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl text-xs text-slate-700 leading-relaxed">
                <span className="font-semibold text-slate-900 block mb-0.5">Status Update:</span>
                {widgetData.message}
              </div>
            )}

            {/* Conversational Chat Log */}
            {chatMessages.length > 0 && (
              <div className="space-y-2 border-t border-slate-100 pt-3">
                <span className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">Chat History</span>
                <div className="space-y-2">
                  {chatMessages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex items-start space-x-2 text-xs ${
                        msg.sender === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      {msg.sender === 'coinsy' && (
                        <div className="bg-indigo-100 text-indigo-700 p-1 rounded-full shrink-0">
                          <Bot className="w-3.5 h-3.5" />
                        </div>
                      )}
                      <div
                        className={`p-2.5 rounded-xl max-w-[82%] leading-relaxed ${
                          msg.sender === 'user'
                            ? 'bg-indigo-600 text-white rounded-br-none font-medium'
                            : 'bg-slate-100 text-slate-800 rounded-bl-none border border-slate-200'
                        }`}
                      >
                        {msg.text}
                      </div>
                      {msg.sender === 'user' && (
                        <div className="bg-slate-200 text-slate-600 p-1 rounded-full shrink-0">
                          <UserIcon className="w-3.5 h-3.5" />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* "Ask Coinsy" Companion Input Form */}
          <form onSubmit={handleAskCoinsy} className="border-t border-slate-200 p-3 bg-slate-50 flex items-center space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask Coinsy about budgets or advice..."
              disabled={isAsking}
              className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isAsking}
              className="bg-indigo-600 hover:bg-indigo-700 text-white p-2 rounded-lg transition-colors disabled:opacity-40 shrink-0"
              title="Send to Coinsy"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>
      )}

      {/* Floating Coinsy Mascot Avatar Button */}
      <CoinsyMascotAvatar
        mood={currentMood}
        isWiggling={isWiggling}
        isWelcome={isWelcome}
        size={60}
        onClick={handleMascotClick}
      />
    </div>
  );
};

export default CoinsyWidget;
