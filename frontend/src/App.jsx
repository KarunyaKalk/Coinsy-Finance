import React from 'react';

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6">
      <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center shadow-xl space-y-4">
        <div className="w-16 h-16 bg-gradient-to-tr from-amber-500 to-yellow-300 rounded-full mx-auto flex items-center justify-center text-3xl font-extrabold text-slate-950 shadow-lg shadow-amber-500/20">
          ₹
        </div>
        <h1 className="text-3xl font-bold text-slate-100 tracking-tight">Coinsy Finance</h1>
        <p className="text-slate-400 text-sm">
          LLM-powered personal finance tracker with your friendly financial mascot.
        </p>
        <div className="pt-4 border-t border-slate-800 flex justify-between items-center text-xs text-slate-500">
          <span>Backend: FastAPI + SQLite</span>
          <span>Frontend: React + Vite</span>
        </div>
      </div>
    </div>
  );
}
