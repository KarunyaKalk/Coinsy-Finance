import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { settingsApi } from '../api/client';
import { Settings, Sliders, Shield, Bell, CheckCircle2, Save, Key, Globe } from 'lucide-react';

export const SettingsPage = () => {
  const { user } = useAuth();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Settings State
  const [scanFrequency, setScanFrequency] = useState('6h');
  const [atsThreshold, setAtsThreshold] = useState(75.0);
  const [dailyAppCap, setDailyAppCap] = useState(15);
  const [dailyEmailCap, setDailyEmailCap] = useState(5);
  const [activePlatforms, setActivePlatforms] = useState({
    linkedin: true,
    indeed: true,
    glassdoor: false,
    wellfound: true,
    ziprecruiter: false,
  });
  const [platformCredentials, setPlatformCredentials] = useState({
    linkedin: '',
    indeed: '',
    wellfound: '',
  });
  const [telegramWebhookUrl, setTelegramWebhookUrl] = useState('');
  const [emailNotificationAddress, setEmailNotificationAddress] = useState('');

  const loadSettings = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await settingsApi.getSettings(user.id);
      setScanFrequency(data.scan_frequency || '6h');
      setAtsThreshold(data.ats_threshold || 75.0);
      setDailyAppCap(data.daily_app_cap || 15);
      setDailyEmailCap(data.daily_email_cap || 5);
      if (data.active_platforms) setActivePlatforms(data.active_platforms);
      if (data.platform_credentials) setPlatformCredentials(data.platform_credentials);
      setTelegramWebhookUrl(data.telegram_webhook_url || '');
      setEmailNotificationAddress(data.email_notification_address || '');
    } catch (err) {
      console.error('Error loading settings:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, [user]);

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    try {
      await settingsApi.updateSettings(user.id, {
        scan_frequency: scanFrequency,
        ats_threshold: parseFloat(atsThreshold),
        daily_app_cap: parseInt(dailyAppCap),
        daily_email_cap: parseInt(dailyEmailCap),
        active_platforms: activePlatforms,
        platform_credentials: platformCredentials,
        telegram_webhook_url: telegramWebhookUrl,
        email_notification_address: emailNotificationAddress,
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error('Error saving settings:', err);
    } finally {
      setSaving(false);
    }
  };

  const handlePlatformToggle = (platformKey) => {
    setActivePlatforms((prev) => ({
      ...prev,
      [platformKey]: !prev[platformKey],
    }));
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Central Application Settings</h1>
          <p className="text-sm text-slate-500">
            Configure scan frequencies, ATS score thresholds, daily caps, platform credentials, and webhook alerts.
          </p>
        </div>

        {saveSuccess && (
          <div className="flex items-center space-x-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 px-3 py-1.5 rounded-lg text-xs font-bold animate-fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Settings Saved!</span>
          </div>
        )}
      </div>

      {loading ? (
        <div className="text-xs text-slate-400 py-12 text-center bg-white border border-slate-200 rounded-xl">
          Loading settings configuration...
        </div>
      ) : (
        <form onSubmit={handleSaveSettings} className="space-y-6">
          {/* Section 1: Automation Parameters & Caps */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
            <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
              <Sliders className="w-5 h-5 text-indigo-600" />
              <h2 className="text-base font-bold text-slate-900">Automation Parameters & Daily Caps</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Job Scrape Scan Frequency
                </label>
                <select
                  value={scanFrequency}
                  onChange={(e) => setScanFrequency(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="1h">Every 1 Hour (High Frequency)</option>
                  <option value="6h">Every 6 Hours (Recommended)</option>
                  <option value="12h">Every 12 Hours</option>
                  <option value="24h">Daily (24 Hours)</option>
                </select>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="block text-xs font-semibold text-slate-700 uppercase">
                    ATS Score Match Threshold
                  </label>
                  <span className="text-xs font-bold text-indigo-600">{atsThreshold}% Match</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="95"
                  step="5"
                  value={atsThreshold}
                  onChange={(e) => setAtsThreshold(e.target.value)}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  Jobs with ATS resume match scores below this threshold will be flagged for review.
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Daily Auto-Application Cap
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={dailyAppCap}
                  onChange={(e) => setDailyAppCap(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Daily Cold-Email Outreach Cap
                </label>
                <input
                  type="number"
                  min="0"
                  max="50"
                  value={dailyEmailCap}
                  onChange={(e) => setDailyEmailCap(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Section 2: Platform Credentials & Active/Inactive Toggles */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
            <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
              <Globe className="w-5 h-5 text-indigo-600" />
              <h2 className="text-base font-bold text-slate-900">Platform Credentials & Active Toggles</h2>
            </div>

            <div className="space-y-4">
              {[
                { key: 'linkedin', name: 'LinkedIn Jobs', placeholder: 'Session Token / API Credential' },
                { key: 'indeed', name: 'Indeed', placeholder: 'Account Token' },
                { key: 'glassdoor', name: 'Glassdoor', placeholder: 'API Credential' },
                { key: 'wellfound', name: 'Wellfound (AngelList)', placeholder: 'Auth Token' },
                { key: 'ziprecruiter', name: 'ZipRecruiter', placeholder: 'API Key' },
              ].map((plat) => {
                const isActive = activePlatforms[plat.key] || false;
                const credVal = platformCredentials[plat.key] || '';

                return (
                  <div
                    key={plat.key}
                    className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 border border-slate-200 rounded-lg bg-slate-50/50"
                  >
                    <div className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={isActive}
                        onChange={() => handlePlatformToggle(plat.key)}
                        className="w-4 h-4 text-indigo-600 rounded cursor-pointer"
                      />
                      <span className="font-semibold text-slate-800 text-sm">{plat.name}</span>
                    </div>

                    <div className="flex items-center space-x-2 w-full sm:w-80">
                      <Key className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <input
                        type="password"
                        value={credVal}
                        onChange={(e) =>
                          setPlatformCredentials({ ...platformCredentials, [plat.key]: e.target.value })
                        }
                        placeholder={plat.placeholder}
                        disabled={!isActive}
                        className="w-full px-3 py-1.5 border border-slate-300 rounded text-xs disabled:bg-slate-100 disabled:opacity-50"
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section 3: Webhook Alerts & Notification Channels */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
            <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
              <Bell className="w-5 h-5 text-indigo-600" />
              <h2 className="text-base font-bold text-slate-900">Webhook Alerts & Notifications</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Telegram Bot Webhook URL
                </label>
                <input
                  type="url"
                  value={telegramWebhookUrl}
                  onChange={(e) => setTelegramWebhookUrl(e.target.value)}
                  placeholder="https://api.telegram.org/bot<TOKEN>/sendMessage"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Alert Email Address
                </label>
                <input
                  type="email"
                  value={emailNotificationAddress}
                  onChange={(e) => setEmailNotificationAddress(e.target.value)}
                  placeholder="user@example.com"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Submit Action */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="flex items-center space-x-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-bold shadow-md transition-all disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? 'Saving Changes...' : 'Save All Settings'}</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default SettingsPage;
