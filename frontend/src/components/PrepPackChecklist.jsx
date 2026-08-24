import React, { useState } from 'react';
import { CheckSquare, Square, Save, Sparkles, Building, Briefcase, FileText, CheckCircle2 } from 'lucide-react';

export const PrepPackChecklist = ({ prepPack, onItemUpdate }) => {
  const [filter, setFilter] = useState('all'); // all | technical | behavioral | star_answer | company_notes
  const [itemNotes, setItemNotes] = useState({});
  const [savingItemIds, setSavingItemIds] = useState(new Set());

  if (!prepPack) return null;

  const { items = [], company_context, resume_overlap_analysis, completed_count, total_count, is_generated_by_llm } = prepPack;

  const filteredItems = items.filter((item) => {
    if (filter === 'all') return true;
    return item.item_type === filter;
  });

  const progressPct = total_count > 0 ? Math.round((completed_count / total_count) * 100) : 0;

  const handleToggleCheck = async (item) => {
    const newStatus = !item.is_completed;
    await onItemUpdate(item.id, {
      is_completed: newStatus,
      user_notes: itemNotes[item.id] !== undefined ? itemNotes[item.id] : item.user_notes,
    });
  };

  const handleSaveNotes = async (item) => {
    const currentNotes = itemNotes[item.id] !== undefined ? itemNotes[item.id] : item.user_notes;
    setSavingItemIds((prev) => new Set(prev).add(item.id));
    try {
      await onItemUpdate(item.id, {
        is_completed: item.is_completed,
        user_notes: currentNotes,
      });
    } finally {
      setSavingItemIds((prev) => {
        const next = new Set(prev);
        next.delete(item.id);
        return next;
      });
    }
  };

  const getItemBadgeClass = (type) => {
    switch (type) {
      case 'technical':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'behavioral':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'star_answer':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Overview & Progress Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-slate-900">Tailored Interview Prep Pack</h2>
              {is_generated_by_llm && (
                <span className="inline-flex items-center text-[10px] bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-semibold border border-indigo-200">
                  <Sparkles className="w-3 h-3 mr-1 text-indigo-600" /> Claude AI Generated
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Check off questions and STAR stories as you prepare. Add your custom notes per item.
            </p>
          </div>

          <div className="flex items-center space-x-3 shrink-0">
            <div className="text-right">
              <div className="text-xs font-semibold text-slate-700">
                {completed_count} / {total_count} Completed
              </div>
              <div className="text-[10px] text-slate-400 font-medium">{progressPct}% Readiness</div>
            </div>
            <div className="w-24 bg-slate-100 h-3 rounded-full overflow-hidden border border-slate-200">
              <div className="bg-emerald-500 h-full rounded-full transition-all duration-300" style={{ width: `${progressPct}%` }} />
            </div>
          </div>
        </div>

        {/* Company Context & Resume Overlap Box */}
        {(company_context || resume_overlap_analysis) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-slate-100 pt-4 text-xs">
            {company_context && (
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 space-y-1">
                <div className="font-semibold text-slate-800 flex items-center space-x-1">
                  <Building className="w-3.5 h-3.5 text-indigo-600" />
                  <span>Company Context & Focus</span>
                </div>
                <p className="text-slate-600 leading-relaxed">{company_context}</p>
              </div>
            )}

            {resume_overlap_analysis && (
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 space-y-1">
                <div className="font-semibold text-slate-800 flex items-center space-x-1">
                  <Briefcase className="w-3.5 h-3.5 text-indigo-600" />
                  <span>Resume Overlap & Gap Analysis</span>
                </div>
                <p className="text-slate-600 leading-relaxed">{resume_overlap_analysis}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Checklist Filter Tabs */}
      <div className="flex items-center space-x-1 border-b border-slate-200 text-xs font-semibold overflow-x-auto pb-1">
        {[
          { key: 'all', label: `All Items (${items.length})` },
          { key: 'technical', label: 'Technical' },
          { key: 'behavioral', label: 'Behavioral' },
          { key: 'star_answer', label: 'STAR Draft Answers' },
          { key: 'company_notes', label: 'Company Notes' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`px-3 py-2 rounded-t-lg transition-colors border-b-2 whitespace-nowrap ${
              filter === tab.key
                ? 'border-indigo-600 text-indigo-600 font-bold bg-white'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Prep Pack Checklist Items List */}
      <div className="space-y-4">
        {filteredItems.length > 0 ? (
          filteredItems.map((item) => {
            const isCompleted = item.is_completed;
            const noteVal = itemNotes[item.id] !== undefined ? itemNotes[item.id] : item.user_notes || '';
            const isSaving = savingItemIds.has(item.id);

            return (
              <div
                key={item.id}
                className={`bg-white border rounded-xl p-5 shadow-sm space-y-3 transition-all ${
                  isCompleted ? 'border-emerald-300 bg-emerald-50/20' : 'border-slate-200'
                }`}
              >
                {/* Item Header & Tick Checkbox */}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start space-x-3">
                    <button
                      onClick={() => handleToggleCheck(item)}
                      className="mt-0.5 text-slate-400 hover:text-emerald-600 transition-colors shrink-0"
                    >
                      {isCompleted ? (
                        <CheckSquare className="w-5 h-5 text-emerald-600 fill-emerald-50" />
                      ) : (
                        <Square className="w-5 h-5 text-slate-400" />
                      )}
                    </button>

                    <div className="space-y-1">
                      <div className="flex items-center space-x-2 flex-wrap gap-1">
                        <span
                          className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${getItemBadgeClass(
                            item.item_type
                          )}`}
                        >
                          {item.item_type.replace('_', ' ')}
                        </span>
                        <h3
                          className={`font-semibold text-sm ${
                            isCompleted ? 'line-through text-slate-500' : 'text-slate-900'
                          }`}
                        >
                          {item.title}
                        </h3>
                      </div>
                      <p className="text-xs text-slate-700 font-medium leading-relaxed">{item.question}</p>
                    </div>
                  </div>
                </div>

                {/* STAR Answer Structured Cards */}
                {item.item_type === 'star_answer' && (
                  <div className="bg-amber-50/60 border border-amber-200/80 rounded-lg p-3 text-xs space-y-2 ml-8">
                    <div className="font-bold text-amber-900 uppercase text-[10px] tracking-wider">STAR Answer Framework (Resume Matched)</div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-800">
                      <div>
                        <span className="font-bold text-slate-900">Situation: </span>
                        <span>{item.star_situation}</span>
                      </div>
                      <div>
                        <span className="font-bold text-slate-900">Task: </span>
                        <span>{item.star_task}</span>
                      </div>
                      <div className="sm:col-span-2">
                        <span className="font-bold text-slate-900">Action (Resume Bullets): </span>
                        <span>{item.star_action}</span>
                      </div>
                      <div className="sm:col-span-2 text-emerald-800 font-semibold">
                        <span className="font-bold text-slate-900">Result: </span>
                        <span>{item.star_result}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Per-Item Notes Field */}
                <div className="ml-8 space-y-1 pt-1">
                  <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500">
                    <span>My Custom Notes & Interview Reminders</span>
                    <button
                      onClick={() => handleSaveNotes(item)}
                      disabled={isSaving}
                      className="flex items-center space-x-1 text-indigo-600 hover:text-indigo-800 transition-colors font-medium disabled:opacity-50"
                    >
                      <Save className="w-3 h-3" />
                      <span>{isSaving ? 'Saving...' : 'Save Notes'}</span>
                    </button>
                  </div>
                  <textarea
                    rows={2}
                    value={noteVal}
                    onChange={(e) => setItemNotes({ ...itemNotes, [item.id]: e.target.value })}
                    placeholder="Add your own notes, talking points, or questions to ask interviewers for this item..."
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50 text-slate-800"
                  />
                </div>
              </div>
            );
          })
        ) : (
          <div className="bg-white border border-dashed border-slate-200 rounded-xl p-8 text-center text-xs text-slate-400">
            No items found for selected filter.
          </div>
        )}
      </div>
    </div>
  );
};

export default PrepPackChecklist;
