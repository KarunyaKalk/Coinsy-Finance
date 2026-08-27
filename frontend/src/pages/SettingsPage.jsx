import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { categoriesApi } from '../api/client';
import { User, Shield, Tag, LogOut, Bot, VolumeX, Flame } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const SettingsPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  // Coinsy Mascot Settings
  const [reduceCoinsy, setReduceCoinsy] = useState(() => {
    return localStorage.getItem('coinsy_reduce_notifications') === 'true';
  });
  const [roastMode, setRoastMode] = useState(() => {
    return localStorage.getItem('coinsy_roast_mode') === 'true';
  });

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const data = await categoriesApi.listCategories(user?.id);
        setCategories(data);
      } catch (err) {
        console.error('Failed to load categories:', err);
      } finally {
        setLoading(false);
      }
    };
    if (user) loadCategories();
  }, [user]);

  const handleToggleReduceCoinsy = (e) => {
    const checked = e.target.checked;
    setReduceCoinsy(checked);
    localStorage.setItem('coinsy_reduce_notifications', checked ? 'true' : 'false');
  };

  const handleToggleRoastMode = (e) => {
    const checked = e.target.checked;
    setRoastMode(checked);
    localStorage.setItem('coinsy_roast_mode', checked ? 'true' : 'false');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings & Account</h1>
        <p className="text-sm text-slate-500">Manage your profile, Coinsy companion behavior, and categories.</p>
      </div>

      {/* User Profile Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-center space-x-3 border-b border-slate-100 pb-4">
          <div className="bg-indigo-50 text-indigo-600 p-3 rounded-full">
            <User className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-900">{user?.full_name || 'Coinsy User'}</h2>
            <p className="text-xs text-slate-500">{user?.email}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-slate-400 block uppercase">User ID</span>
            <span className="font-semibold text-slate-700">#{user?.id}</span>
          </div>
          <div>
            <span className="text-slate-400 block uppercase">Account Status</span>
            <span className="font-semibold text-emerald-600">Active</span>
          </div>
        </div>
      </div>

      {/* Coinsy Mascot & Personality Settings */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
          <Bot className="w-4 h-4 text-indigo-600" />
          <h2 className="text-base font-semibold text-slate-900">Coinsy Companion Settings</h2>
        </div>

        <div className="space-y-4">
          {/* Reduce Coinsy Setting */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5 pr-4">
              <div className="flex items-center space-x-1.5 font-medium text-sm text-slate-800">
                <VolumeX className="w-4 h-4 text-slate-500" />
                <span>Reduce Coinsy Proactive Bubbles</span>
              </div>
              <p className="text-xs text-slate-500">
                Disables automatic speech bubble popups and notifications. Click-to-ask companion chat remains available.
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer shrink-0">
              <input
                type="checkbox"
                checked={reduceCoinsy}
                onChange={handleToggleReduceCoinsy}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
            </label>
          </div>

          {/* Roast Mode Toggle */}
          <div className="flex items-center justify-between border-t border-slate-100 pt-3">
            <div className="space-y-0.5 pr-4">
              <div className="flex items-center space-x-1.5 font-medium text-sm text-slate-800">
                <Flame className="w-4 h-4 text-amber-500" />
                <span>Roast Mode (Humorous Sarcastic Tips)</span>
              </div>
              <p className="text-xs text-slate-500">
                Changes Coinsy's daily tips and chat responses to funny, lighthearted financial roasts.
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer shrink-0">
              <input
                type="checkbox"
                checked={roastMode}
                onChange={handleToggleRoastMode}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Categories List */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
          <Tag className="w-4 h-4 text-indigo-600" />
          <h2 className="text-base font-semibold text-slate-900">Spending Categories</h2>
        </div>

        {loading ? (
          <div className="text-xs text-slate-400">Loading categories...</div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {categories.map((cat) => (
              <div key={cat.id || cat.name} className="flex items-center space-x-2 border border-slate-100 bg-slate-50 p-2.5 rounded-lg">
                {cat.color && (
                  <span
                    className="w-3 h-3 rounded-full shrink-0"
                    style={{ backgroundColor: cat.color }}
                  />
                )}
                <span className="text-xs font-medium text-slate-800">{cat.name}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Account Security */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
          <Shield className="w-4 h-4 text-indigo-600" />
          <h2 className="text-base font-semibold text-slate-900">Account Security</h2>
        </div>

        <button
          onClick={handleLogout}
          className="flex items-center space-x-2 text-rose-600 hover:text-rose-700 bg-rose-50 border border-rose-200 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Sign Out of Coinsy</span>
        </button>
      </div>
    </div>
  );
};

export default SettingsPage;
