import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { auditApi } from '../api/client';
import { ShieldAlert, Activity, CheckCircle2, AlertTriangle, XCircle, Lock, RefreshCw, Filter } from 'lucide-react';

export const AuditFeed = () => {
  const { user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [actionType, setActionType] = useState('all');
  const [isSimulating, setIsSimulating] = useState(false);

  const fetchLogs = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await auditApi.getAuditLogs(user.id, actionType, statusFilter, 50);
      setLogs(data);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [user, statusFilter, actionType]);

  const handleSimulateBlock = async () => {
    if (!user) return;
    setIsSimulating(true);
    try {
      await auditApi.triggerBlockAlert(user.id, 'LinkedIn', 'CAPTCHA challenge detected during automated scrape');
      fetchLogs();
    } catch (err) {
      console.error('Error simulating block alert:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'success':
        return (
          <span className="inline-flex items-center text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" /> SUCCESS
          </span>
        );
      case 'warning':
        return (
          <span className="inline-flex items-center text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full border border-amber-200">
            <AlertTriangle className="w-3 h-3 mr-1 text-amber-600" /> WARNING
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center text-[10px] font-bold bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full border border-rose-200">
            <XCircle className="w-3 h-3 mr-1 text-rose-600" /> FAILED
          </span>
        );
      case 'blocked':
        return (
          <span className="inline-flex items-center text-[10px] font-bold bg-purple-100 text-purple-900 px-2 py-0.5 rounded-full border border-purple-300 ring-2 ring-purple-400/20">
            <Lock className="w-3 h-3 mr-1 text-purple-600" /> CAPTCHA BLOCKED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center text-[10px] font-medium bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-indigo-600" />
          <div>
            <h2 className="text-base font-bold text-slate-900">Agent Activity & Audit Trail</h2>
            <p className="text-xs text-slate-500">Transparent execution log for all scrapes, applications, and block alerts</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleSimulateBlock}
            disabled={isSimulating}
            className="flex items-center space-x-1 px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-lg text-xs font-semibold transition-colors disabled:opacity-50"
            title="Test CAPTCHA block alert engine"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-purple-600" />
            <span>Simulate Block Alert</span>
          </button>

          <button
            onClick={fetchLogs}
            className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors"
            title="Refresh logs"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex items-center justify-between flex-wrap gap-2 text-xs">
        <div className="flex items-center space-x-1.5">
          <span className="text-slate-500 font-medium">Status:</span>
          {['all', 'success', 'warning', 'failed', 'blocked'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-semibold capitalize transition-colors ${
                statusFilter === st
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-1.5">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={actionType}
            onChange={(e) => setActionType(e.target.value)}
            className="px-2 py-1 border border-slate-300 rounded-md text-xs bg-white text-slate-700 font-medium"
          >
            <option value="all">All Action Types</option>
            <option value="scrape_run">Scrape Runs</option>
            <option value="resume_generation">Resume Generations</option>
            <option value="ats_score">ATS Score Checks</option>
            <option value="application_submission">Applications</option>
            <option value="email_sent">Cold Emails</option>
            <option value="captcha_blocked">CAPTCHA Blocks</option>
          </select>
        </div>
      </div>

      {/* Activity Logs Timeline */}
      {loading ? (
        <div className="text-xs text-slate-400 py-8 text-center">Loading audit activity feed...</div>
      ) : logs.length > 0 ? (
        <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
          {logs.map((log) => (
            <div
              key={log.id}
              className={`p-3 rounded-lg border text-xs space-y-1 transition-all ${
                log.status === 'blocked' ? 'bg-purple-50/50 border-purple-200' : 'bg-slate-50/50 border-slate-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getStatusBadge(log.status)}
                  {log.platform && (
                    <span className="text-[10px] font-bold bg-slate-200 text-slate-700 px-1.5 py-0.2 rounded">
                      {log.platform}
                    </span>
                  )}
                  <span className="font-bold text-slate-900">{log.title}</span>
                </div>

                <span className="text-[10px] text-slate-400 font-mono">
                  {new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
              </div>

              {log.details && <p className="text-slate-600 leading-relaxed pl-1">{log.details}</p>}
            </div>
          ))}
        </div>
      ) : (
        <div className="border border-dashed border-slate-200 rounded-xl p-8 text-center text-xs text-slate-400">
          No audit log events match selected filters.
        </div>
      )}
    </div>
  );
};

export default AuditFeed;
